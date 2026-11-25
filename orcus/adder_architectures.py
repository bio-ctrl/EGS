"""Bit-level adder architecture generators for reproducible design-space exploration.

This is a deliberately small architecture family, not a claim of a new adder.
It creates two structurally different implementations of the same unsigned
addition function so ORCUS can compare correctness, logic depth, fanout, and
independent synthesis results.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class LogicNode:
    node_id: str
    op: str
    args: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ArchitectureMetrics:
    gate_count: int
    logic_depth: int
    max_fanout: int


@dataclass(frozen=True, slots=True)
class AdderArchitecture:
    name: str
    width: int
    nodes: tuple[LogicNode, ...]
    sum_bits: tuple[str, ...]
    carry_out: str

    def _input_values(self, a: int, b: int) -> dict[str, int]:
        limit = (1 << self.width) - 1
        if not 0 <= a <= limit or not 0 <= b <= limit:
            raise ValueError(f"inputs must be unsigned {self.width}-bit integers")
        values = {"0": 0, "1": 1}
        for bit in range(self.width):
            values[f"a{bit}"] = (a >> bit) & 1
            values[f"b{bit}"] = (b >> bit) & 1
        return values

    def evaluate(self, a: int, b: int) -> int:
        values = self._input_values(a, b)
        for node in self.nodes:
            x = values[node.args[0]]
            y = values[node.args[1]]
            if node.op == "AND":
                values[node.node_id] = x & y
            elif node.op == "OR":
                values[node.node_id] = x | y
            elif node.op == "XOR":
                values[node.node_id] = x ^ y
            else:
                raise ValueError(f"unsupported operation: {node.op}")
        result = sum(values[name] << bit for bit, name in enumerate(self.sum_bits))
        return result | (values[self.carry_out] << self.width)

    def metrics(self) -> ArchitectureMetrics:
        depths: dict[str, int] = {"0": 0, "1": 0}
        fanout: dict[str, int] = {}
        for bit in range(self.width):
            depths[f"a{bit}"] = 0
            depths[f"b{bit}"] = 0
        for node in self.nodes:
            depths[node.node_id] = 1 + max(depths[arg] for arg in node.args)
            for arg in node.args:
                fanout[arg] = fanout.get(arg, 0) + 1
        for name in (*self.sum_bits, self.carry_out):
            fanout[name] = fanout.get(name, 0) + 1
        output_depth = max(depths[name] for name in (*self.sum_bits, self.carry_out))
        return ArchitectureMetrics(
            gate_count=len(self.nodes),
            logic_depth=output_depth,
            max_fanout=max(fanout.values(), default=0),
        )

    def emit_verilog(self, module_name: str | None = None) -> str:
        module = module_name or f"orcus_{self.name}_{self.width}"
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", module):
            raise ValueError("module name must be a valid Verilog identifier")
        lines = [
            f"module {module}(input [{self.width - 1}:0] a, b, output [{self.width}:0] sum);"
        ]
        for node in self.nodes:
            lines.append(f"  wire {node.node_id};")
        def operand(name: str) -> str:
            if name in {"0", "1"}:
                return f"1'b{name}"
            if name.startswith("a") and name[1:].isdigit():
                return f"a[{int(name[1:])}]"
            if name.startswith("b") and name[1:].isdigit():
                return f"b[{int(name[1:])}]"
            return name
        symbols = {"AND": "&", "OR": "|", "XOR": "^"}
        for node in self.nodes:
            left, right = (operand(arg) for arg in node.args)
            lines.append(f"  assign {node.node_id} = {left} {symbols[node.op]} {right};")
        for bit, name in enumerate(self.sum_bits):
            lines.append(f"  assign sum[{bit}] = {operand(name)};")
        lines.append(f"  assign sum[{self.width}] = {operand(self.carry_out)};")
        lines.append("endmodule")
        return "\n".join(lines) + "\n"


class _Builder:
    def __init__(self) -> None:
        self.nodes: list[LogicNode] = []
        self.serial = 0

    def gate(self, op: str, left: str, right: str) -> str:
        if op not in {"AND", "OR", "XOR"}:
            raise ValueError(f"unsupported gate: {op}")
        name = f"n{self.serial}"
        self.serial += 1
        self.nodes.append(LogicNode(name, op, (left, right)))
        return name


def build_ripple_carry_adder(width: int) -> AdderArchitecture:
    """Build the conventional serial carry-propagation architecture."""
    if not 1 <= width <= 64:
        raise ValueError("width must be between 1 and 64")
    b = _Builder()
    carry = "0"
    sums = []
    for bit in range(width):
        p = b.gate("XOR", f"a{bit}", f"b{bit}")
        g = b.gate("AND", f"a{bit}", f"b{bit}")
        sums.append(b.gate("XOR", p, carry))
        carry = b.gate("OR", g, b.gate("AND", p, carry))
    return AdderArchitecture("ripple", width, tuple(b.nodes), tuple(sums), carry)


def build_kogge_stone_adder(width: int) -> AdderArchitecture:
    """Build a parallel-prefix adder with logarithmic prefix stages."""
    if not 1 <= width <= 64:
        raise ValueError("width must be between 1 and 64")
    b = _Builder()
    p = [b.gate("XOR", f"a{i}", f"b{i}") for i in range(width)]
    g = [b.gate("AND", f"a{i}", f"b{i}") for i in range(width)]
    distance = 1
    while distance < width:
        old_p, old_g = p[:], g[:]
        for bit in range(distance, width):
            combined_g = b.gate("AND", old_p[bit], old_g[bit - distance])
            g[bit] = b.gate("OR", old_g[bit], combined_g)
            p[bit] = b.gate("AND", old_p[bit], old_p[bit - distance])
        distance *= 2
    carry = ["0", *g[:-1]]
    sums = [b.gate("XOR", p[i], carry[i]) for i in range(width)]
    return AdderArchitecture("kogge_stone", width, tuple(b.nodes), tuple(sums), g[-1])
