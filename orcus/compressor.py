"""Bit-heap compressor-network generation for multi-operand unsigned addition.

Wallace and Dadda are reference schedules. The search variants are bounded,
deterministic alternatives; none are claimed to be novel or physically optimal.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import ceil, log2


@dataclass(frozen=True)
class Gate:
    name: str
    op: str
    args: tuple[str, ...]


@dataclass(frozen=True)
class CompressorNetwork:
    schedule: str
    operand_count: int
    width: int
    output_width: int
    gates: tuple[Gate, ...]
    output_bits: tuple[str, ...]

    def evaluate(self, operands: tuple[int, ...]) -> int:
        if len(operands) != self.operand_count:
            raise ValueError("wrong operand count")
        limit = (1 << self.width) - 1
        if any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= limit for v in operands):
            raise ValueError("operand outside unsigned input width")
        values = {"0": 0, "1": 1}
        for i, value in enumerate(operands):
            for bit in range(self.width):
                values[f"x{i}_{bit}"] = (value >> bit) & 1
        for gate in self.gates:
            a = [values[x] for x in gate.args]
            if gate.op == "XOR": value = a[0] ^ a[1]
            elif gate.op == "AND": value = a[0] & a[1]
            elif gate.op == "OR": value = a[0] | a[1]
            else: raise ValueError(f"unknown gate {gate.op}")
            values[gate.name] = value
        return sum(values[name] << bit for bit, name in enumerate(self.output_bits))

    def metrics(self) -> dict[str, int]:
        depth = {"0": 0, "1": 0}
        fanout = {}
        for i in range(self.operand_count):
            for bit in range(self.width):
                name = f"x{i}_{bit}"
                depth[name] = 0
                fanout[name] = 0
        for gate in self.gates:
            depth[gate.name] = 1 + max(depth[x] for x in gate.args)
            fanout[gate.name] = 0
            for x in gate.args:
                fanout[x] = fanout.get(x, 0) + 1
        for name in self.output_bits:
            fanout[name] = fanout.get(name, 0) + 1
        return {"gate_count": len(self.gates),
                "logic_depth": max(depth[x] for x in self.output_bits),
                "max_fanout": max(fanout.values(), default=0)}

    def emit_verilog(self, module_name: str = "orcus_compressor") -> str:
        if not module_name.replace("_", "a").isalnum() or module_name[0].isdigit():
            raise ValueError("invalid module name")
        ports = [f"input [{self.width-1}:0] x{i}" for i in range(self.operand_count)]
        ports.append(f"output [{self.output_width-1}:0] sum")
        lines = [f"module {module_name}({', '.join(p.split()[-1] for p in ports)});"]
        lines.extend(f"  {p};" for p in ports)
        lines.extend(f"  wire {g.name};" for g in self.gates)
        sym = {"XOR": "^", "AND": "&", "OR": "|"}
        for g in self.gates:
            def ref(s):
                if s in {"0", "1"}: return f"1'b{s}"
                if s.startswith("x") and "_" in s:
                    operand, bit = s[1:].split("_")
                    return f"x{operand}[{bit}]"
                return s
            lines.append(f"  assign {g.name} = {ref(g.args[0])} {sym[g.op]} {ref(g.args[1])};")
        refs = []
        for s in self.output_bits:
            if s in {"0", "1"}: refs.append(f"1'b{s}")
            elif s.startswith("x") and "_" in s:
                operand, bit = s[1:].split("_")
                refs.append(f"x{operand}[{bit}]")
            else: refs.append(s)
        lines.append(f"  assign sum = {{{', '.join(reversed(refs))}}};")
        lines.append("endmodule")
        return "\n".join(lines) + "\n"


class _Builder:
    def __init__(self):
        self.gates = []
        self.serial = 0

    def gate(self, op, a, b):
        name = f"g{self.serial}"
        self.serial += 1
        self.gates.append(Gate(name, op, (a, b)))
        return name

    def full_adder(self, a, b, c):
        p = self.gate("XOR", a, b)
        s = self.gate("XOR", p, c)
        ab = self.gate("AND", a, b)
        pc = self.gate("AND", p, c)
        carry = self.gate("OR", ab, pc)
        return s, carry

    def half_adder(self, a, b):
        return self.gate("XOR", a, b), self.gate("AND", a, b)


def _initial_heap(operands, width):
    heap = [[] for _ in range(width + ceil(log2(operands)) + 1)]
    for i in range(operands):
        for bit in range(width):
            heap[bit].append(f"x{i}_{bit}")
    return heap


def _compress_wallace(heap, builder, reverse=False):
    while any(len(col) > 2 for col in heap):
        next_heap = [[] for _ in heap]
        for bit, col in enumerate(heap):
            items = list(reversed(col)) if reverse else list(col)
            groups = len(items) // 3
            for group in range(groups):
                a, b, c = items[group*3:group*3+3]
                s, carry = builder.full_adder(a, b, c)
                next_heap[bit].append(s)
                if bit + 1 < len(heap): next_heap[bit+1].append(carry)
            next_heap[bit].extend(items[groups*3:])
        heap = next_heap
    return heap


def _compress_dadda(heap, builder):
    maximum = max(map(len, heap))
    targets = [2]
    while targets[-1] < maximum:
        targets.append((targets[-1] * 3) // 2)
    for target in reversed(targets[:-1]):
        for bit in range(len(heap)-1):
            while len(heap[bit]) > target:
                if len(heap[bit]) - target >= 2 and len(heap[bit]) >= 3:
                    a, b, c = heap[bit][:3]
                    del heap[bit][:3]
                    s, carry = builder.full_adder(a, b, c)
                else:
                    a, b = heap[bit][:2]
                    del heap[bit][:2]
                    s, carry = builder.half_adder(a, b)
                heap[bit].append(s)
                heap[bit+1].append(carry)
    # Any remaining height above two is handled by a final Wallace pass.
    return _compress_wallace(heap, builder)


def _finish_two_rows(heap, builder, final_adder):
    row0, row1 = [], []
    for col in heap:
        row0.append(col[0] if col else "0")
        row1.append(col[1] if len(col) > 1 else "0")
    if final_adder == "ripple":
        carry = "0"
        out = []
        for a, b in zip(row0, row1):
            s, carry = builder.full_adder(a, b, carry)
            out.append(s)
        out.append(carry)
        return tuple(out)
    p = [builder.gate("XOR", a, b) for a, b in zip(row0, row1)]
    bit_propagate = p[:]
    g = [builder.gate("AND", a, b) for a, b in zip(row0, row1)]
    if final_adder == "kogge_stone":
        distance = 1
        while distance < len(p):
            old_p, old_g = p[:], g[:]
            for bit in range(distance, len(p)):
                combined = builder.gate("AND", old_p[bit], old_g[bit-distance])
                g[bit] = builder.gate("OR", old_g[bit], combined)
                p[bit] = builder.gate("AND", old_p[bit], old_p[bit-distance])
            distance *= 2
    elif final_adder == "sklansky":
        distance = 1
        while distance < len(p):
            old_p, old_g = p[:], g[:]
            for bit in range(len(p)):
                if bit % (2 * distance) >= distance:
                    lower = (bit // (2 * distance)) * (2 * distance) + distance - 1
                    combined = builder.gate("AND", old_p[bit], old_g[lower])
                    g[bit] = builder.gate("OR", old_g[bit], combined)
                    p[bit] = builder.gate("AND", old_p[bit], old_p[lower])
            distance *= 2
    else:
        raise ValueError("final_adder must be ripple, kogge_stone, or sklansky")
    carries = ["0", *g[:-1]]
    sums = [builder.gate("XOR", bit_propagate[i], carries[i]) for i in range(len(p))]
    return tuple([*sums, g[-1]])


def build_compressor_network(operand_count: int, width: int, schedule: str = "wallace",
                             final_adder: str = "ripple") -> CompressorNetwork:
    if not 3 <= operand_count <= 16:
        raise ValueError("operand_count must be between 3 and 16")
    if not 1 <= width <= 32:
        raise ValueError("width must be between 1 and 32")
    if schedule not in {"wallace", "wallace_reverse", "dadda"}:
        raise ValueError("schedule must be wallace, wallace_reverse, or dadda")
    if final_adder not in {"ripple", "kogge_stone", "sklansky"}:
        raise ValueError("final_adder must be ripple, kogge_stone, or sklansky")
    builder = _Builder()
    heap = _initial_heap(operand_count, width)
    heap = (_compress_dadda(heap, builder) if schedule == "dadda"
            else _compress_wallace(heap, builder, schedule == "wallace_reverse"))
    outputs = _finish_two_rows(heap, builder, final_adder)
    output_width = width + ceil(log2(operand_count))
    return CompressorNetwork(schedule + "+" + final_adder, operand_count, width, output_width,
                             tuple(builder.gates), outputs[:output_width])

def verify_exhaustive(network: CompressorNetwork, max_input_bits: int = 16) -> dict:
    total_bits = network.operand_count * network.width
    if total_bits > max_input_bits:
        return {"passed": False, "exhaustive": False, "vectors_checked": 0}
    checked = 0
    ranges = [range(1 << network.width)] * network.operand_count
    for values in product(*ranges):
        checked += 1
        if network.evaluate(values) != sum(values):
            return {"passed": False, "exhaustive": True, "vectors_checked": checked}
    return {"passed": True, "exhaustive": True, "vectors_checked": checked}
