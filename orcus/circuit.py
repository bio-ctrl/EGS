"""Circuit IR, exhaustive evaluator, and technology-independent metrics."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable

from .expression import Expr
from .gates import GATE_LIBRARY, apply_gate
from .truth_table import TruthTable, assignment_to_row


@dataclass(frozen=True, slots=True)
class CircuitNode:
    node_id: str
    op: str
    inputs: tuple[str, ...] = ()
    value: int | None = None


@dataclass(frozen=True, slots=True)
class CircuitMetrics:
    gate_count: int
    logic_depth: int
    max_fanout: int
    input_fanout: tuple[int, ...]
    output_one_density: float
    output_toggle_proxy: float


@dataclass(frozen=True, slots=True)
class Circuit:
    input_count: int
    nodes: tuple[CircuitNode, ...]
    output: str

    @classmethod
    def from_expression(cls, expr: Expr, input_count: int) -> "Circuit":
        if not 1 <= input_count <= 8:
            raise ValueError("input_count must be between 1 and 8")
        nodes: list[CircuitNode] = []
        ids: dict[tuple, str] = {}

        def visit(item: Expr) -> str:
            key = item.structural_key
            if key in ids:
                return ids[key]
            child_ids = tuple(visit(child) for child in item.args)
            node_id = f"n{len(nodes)}"
            nodes.append(CircuitNode(node_id, item.op, child_ids, item.value))
            ids[key] = node_id
            return node_id

        output = visit(expr)
        return cls(input_count, tuple(nodes), output)

    def _evaluate_assignment(self, assignment: tuple[int, ...]) -> dict[str, int]:
        assignment_to_row(assignment, self.input_count)
        values: dict[str, int] = {}
        for node in self.nodes:
            if node.op == "VAR":
                assert node.value is not None
                result = int(bool(assignment[node.value]))
            elif node.op == "CONST":
                result = int(bool(node.value))
            else:
                result = apply_gate(node.op, tuple(values[i] for i in node.inputs), 1)
            values[node.node_id] = result
        return values

    def evaluate(self, assignment: tuple[int, ...] | list[int]) -> int:
        values = self._evaluate_assignment(tuple(assignment))
        return values[self.output]

    def truth_table(self) -> TruthTable:
        bits = 0
        for row, assignment in enumerate(product((0, 1), repeat=self.input_count)):
            bits |= self.evaluate(assignment) << row
        return TruthTable(self.input_count, bits)

    def verify(self, target: TruthTable | None = None) -> bool:
        actual = self.truth_table()
        return True if target is None else actual == target

    def fanout(self) -> dict[str, int]:
        counts = {node.node_id: 0 for node in self.nodes}
        for node in self.nodes:
            for source in node.inputs:
                counts[source] += 1
        counts[self.output] += 1
        return counts

    def to_dict(self) -> dict:
        return {
            "input_count": self.input_count,
            "nodes": [
                {"id": n.node_id, "op": n.op, "inputs": list(n.inputs), "value": n.value}
                for n in self.nodes
            ],
            "output": self.output,
            "truth_table": self.truth_table().hex(),
        }


def measure_circuit(circuit: Circuit) -> CircuitMetrics:
    depth: dict[str, int] = {}
    for node in circuit.nodes:
        if node.op in {"VAR", "CONST"}:
            depth[node.node_id] = 0
        else:
            depth[node.node_id] = 1 + max(depth[src] for src in node.inputs)
    fanout = circuit.fanout()
    table = circuit.truth_table()
    row_count = len(table)
    ones = sum(table.outputs()) / row_count
    toggle_proxy = 2.0 * ones * (1.0 - ones)
    return CircuitMetrics(
        gate_count=sum(n.op in GATE_LIBRARY for n in circuit.nodes),
        logic_depth=depth[circuit.output],
        max_fanout=max(fanout.values(), default=0),
        input_fanout=tuple(
            next((fanout.get(n.node_id, 0) for n in circuit.nodes if n.op == "VAR" and n.value == i), 0)
            for i in range(circuit.input_count)
        ),
        output_one_density=ones,
        output_toggle_proxy=toggle_proxy,
    )
