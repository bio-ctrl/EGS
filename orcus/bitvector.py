"""Typed, width-aware dataflow IR for combinational architecture experiments.

This representation is intentionally technology-independent. It validates
operator widths and topological dependencies, evaluates candidates exactly,
emits synthesizable-style Verilog, and reports structural (not physical) cost.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import re
from typing import Callable, Mapping


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")
_OPERATORS = {"add", "sub", "and", "or", "xor", "not", "mux", "eq", "shl", "shr"}


@dataclass(frozen=True, slots=True)
class DataPort:
    name: str
    width: int


@dataclass(frozen=True, slots=True)
class DataNode:
    node_id: str
    op: str
    inputs: tuple[str, ...]
    width: int
    value: int | None = None


@dataclass(frozen=True, slots=True)
class DataOutput:
    name: str
    source: str
    width: int


@dataclass(frozen=True, slots=True)
class DataflowMetrics:
    operation_count: int
    logic_depth: int
    max_fanout: int
    fanout_by_signal: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class VerificationReport:
    passed: bool
    exhaustive: bool
    vectors_checked: int
    input_bits: int


@dataclass(frozen=True, slots=True)
class BitVectorGraph:
    inputs: tuple[DataPort, ...]
    nodes: tuple[DataNode, ...]
    outputs: tuple[DataOutput, ...]

    def __post_init__(self) -> None:
        if not self.inputs or not self.outputs:
            raise ValueError("a graph needs at least one input and one output")
        names: set[str] = set()
        widths: dict[str, int] = {}
        for port in self.inputs:
            self._check_name(port.name)
            self._check_width(port.width)
            if port.name in names:
                raise ValueError(f"duplicate signal name: {port.name}")
            names.add(port.name)
            widths[port.name] = port.width

        for node in self.nodes:
            self._check_name(node.node_id)
            self._check_width(node.width)
            if node.node_id in names:
                raise ValueError(f"duplicate signal name: {node.node_id}")
            if node.op not in _OPERATORS and node.op != "const":
                raise ValueError(f"unsupported operation: {node.op}")
            if any(source not in widths for source in node.inputs):
                raise ValueError(f"{node.node_id} references an unknown or forward signal")
            self._validate_node(node, widths)
            names.add(node.node_id)
            widths[node.node_id] = node.width

        output_names: set[str] = set()
        for output in self.outputs:
            self._check_name(output.name)
            self._check_width(output.width)
            if output.name in output_names:
                raise ValueError(f"duplicate output name: {output.name}")
            if output.source not in widths:
                raise ValueError(f"output {output.name} references an unknown signal")
            if widths[output.source] != output.width:
                raise ValueError(f"output {output.name} width does not match its source")
            output_names.add(output.name)

    @staticmethod
    def _check_name(name: str) -> None:
        if not _IDENTIFIER.fullmatch(name):
            raise ValueError(f"invalid Verilog identifier: {name!r}")

    @staticmethod
    def _check_width(width: int) -> None:
        if not isinstance(width, int) or isinstance(width, bool) or not 1 <= width <= 64:
            raise ValueError("signal widths must be integers from 1 through 64")

    @staticmethod
    def _validate_node(node: DataNode, widths: Mapping[str, int]) -> None:
        arity = {"const": 0, "not": 1, "add": 2, "sub": 2, "and": 2,
                 "or": 2, "xor": 2, "mux": 3, "eq": 2, "shl": 2, "shr": 2}
        if len(node.inputs) != arity[node.op]:
            raise ValueError(f"{node.op} expects {arity[node.op]} inputs")
        if node.op == "const":
            if node.value is None or not 0 <= node.value < (1 << node.width):
                raise ValueError("constant value must fit its declared width")
            return
        if node.value is not None:
            raise ValueError("only const nodes may define a value")
        source_widths = [widths[source] for source in node.inputs]
        if node.op in {"add", "sub"}:
            if source_widths[0] != source_widths[1] or node.width not in {source_widths[0], source_widths[0] + 1}:
                raise ValueError(f"{node.op} requires equal-width operands and a result width equal to operand width or one bit wider")
        elif node.op in {"and", "or", "xor"}:
            if source_widths != [node.width, node.width]:
                raise ValueError(f"{node.op} requires two operands matching result width")
        elif node.op == "not":
            if source_widths != [node.width]:
                raise ValueError("not requires an operand matching result width")
        elif node.op == "mux":
            if source_widths[0] != 1 or source_widths[1:] != [node.width, node.width]:
                raise ValueError("mux requires a 1-bit select and two result-width data inputs")
        elif node.op == "eq":
            if source_widths[0] != source_widths[1] or node.width != 1:
                raise ValueError("eq requires equal-width operands and a 1-bit result")
        elif node.op in {"shl", "shr"}:
            if source_widths[0] != node.width:
                raise ValueError(f"{node.op} data input must match result width")

    def _widths(self) -> dict[str, int]:
        result = {port.name: port.width for port in self.inputs}
        result.update({node.node_id: node.width for node in self.nodes})
        return result

    def evaluate(self, values: Mapping[str, int]) -> dict[str, int]:
        if set(values) != {port.name for port in self.inputs}:
            raise ValueError("input mapping must contain exactly the declared input names")
        signals: dict[str, int] = {}
        for port in self.inputs:
            value = values[port.name]
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < (1 << port.width):
                raise ValueError(f"input {port.name} is outside its unsigned width")
            signals[port.name] = value
        for node in self.nodes:
            args = [signals[name] for name in node.inputs]
            mask = (1 << node.width) - 1
            if node.op == "const": result = node.value
            elif node.op == "add": result = args[0] + args[1]
            elif node.op == "sub": result = args[0] - args[1]
            elif node.op == "and": result = args[0] & args[1]
            elif node.op == "or": result = args[0] | args[1]
            elif node.op == "xor": result = args[0] ^ args[1]
            elif node.op == "not": result = ~args[0]
            elif node.op == "mux": result = args[1] if args[0] else args[2]
            elif node.op == "eq": result = int(args[0] == args[1])
            elif node.op == "shl": result = args[0] << args[1]
            elif node.op == "shr": result = args[0] >> args[1]
            else: raise AssertionError("validated operator became unsupported")
            signals[node.node_id] = int(result) & mask
        return {output.name: signals[output.source] for output in self.outputs}

    def metrics(self) -> DataflowMetrics:
        depths = {port.name: 0 for port in self.inputs}
        fanout = {name: 0 for name in depths}
        for node in self.nodes:
            depths[node.node_id] = (0 if node.op == "const" else
                                    1 + max((depths[name] for name in node.inputs), default=0))
            fanout[node.node_id] = 0
            for source in node.inputs:
                fanout[source] += 1
        for output in self.outputs:
            fanout[output.source] += 1
        output_depth = max(depths[output.source] for output in self.outputs)
        ordered = tuple(sorted(fanout.items()))
        return DataflowMetrics(
            operation_count=len(self.nodes),
            logic_depth=output_depth,
            max_fanout=max(fanout.values(), default=0),
            fanout_by_signal=ordered,
        )

    def verify_exhaustive(
        self,
        reference: Callable[[Mapping[str, int]], Mapping[str, int]],
        max_input_bits: int = 16,
    ) -> VerificationReport:
        input_bits = sum(port.width for port in self.inputs)
        if input_bits > max_input_bits:
            return VerificationReport(False, False, 0, input_bits)
        checked = 0
        ranges = [range(1 << port.width) for port in self.inputs]
        for vector in product(*ranges):
            assignment = {port.name: value for port, value in zip(self.inputs, vector)}
            if self.evaluate(assignment) != dict(reference(assignment)):
                return VerificationReport(False, True, checked + 1, input_bits)
            checked += 1
        return VerificationReport(True, True, checked, input_bits)

    def emit_verilog(self, module_name: str = "orcus_candidate") -> str:
        self._check_name(module_name)
        declarations = []
        for port in self.inputs:
            declarations.append(f"input {self._range(port.width)}{port.name}")
        for output in self.outputs:
            declarations.append(f"output {self._range(output.width)}{output.name}")
        lines = [f"module {module_name}({', '.join(p.name for p in self.inputs + self.outputs)});"]
        lines.extend(f"  {decl};" for decl in declarations)
        lines.extend(f"  wire {self._range(node.width)}{node.node_id};" for node in self.nodes)
        symbols = {"add": "+", "sub": "-", "and": "&", "or": "|", "xor": "^",
                   "eq": "==", "shl": "<<", "shr": ">>"}
        for node in self.nodes:
            args = list(node.inputs)
            if node.op == "const":
                expression = f"{node.width}'d{node.value}"
            elif node.op == "not":
                expression = f"~{args[0]}"
            elif node.op == "mux":
                expression = f"{args[0]} ? {args[1]} : {args[2]}"
            elif node.op in {"add", "sub"}:
                operand_width = self._widths()[args[0]]
                if node.width > operand_width:
                    pad = node.width - operand_width
                    left = f"{{{{{pad}{{1'b0}}}}, {args[0]}}}"
                    right = f"{{{{{pad}{{1'b0}}}}, {args[1]}}}"
                else:
                    left, right = args
                expression = f"{left} {symbols[node.op]} {right}"
            else:
                expression = f"{args[0]} {symbols[node.op]} {args[1]}"
            lines.append(f"  assign {node.node_id} = {expression};")
        for output in self.outputs:
            lines.append(f"  assign {output.name} = {output.source};")
        lines.append("endmodule")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _range(width: int) -> str:
        return f"[{width - 1}:0] " if width > 1 else ""
