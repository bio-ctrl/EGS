"""Multi-output Boolean networks with structural sharing across outputs.

Unlike the first expression-tree synthesizer, a Network is an explicit DAG.
Identical expression subgraphs are represented once and may feed multiple
consumers or outputs. This module provides the representation and validation
layer needed for later multi-output architecture search; it does not yet
search the multi-output design space.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping

from .circuit import CircuitNode
from .expression import Expr
from .gates import GATE_LIBRARY, apply_gate
from .truth_table import TruthTable, assignment_to_row


@dataclass(frozen=True, slots=True)
class NetworkMetrics:
    unique_gate_count: int
    logic_depth: int
    max_fanout: int
    input_fanout: tuple[int, ...]
    output_one_density: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class CircuitNetwork:
    input_count: int
    nodes: tuple[CircuitNode, ...]
    outputs: tuple[tuple[str, str], ...]

    @classmethod
    def from_expressions(
        cls, expressions: Mapping[str, Expr], input_count: int
    ) -> "CircuitNetwork":
        if not 1 <= input_count <= 8:
            raise ValueError("input_count must be between 1 and 8")
        if not expressions:
            raise ValueError("at least one output expression is required")
        if len(set(expressions)) != len(expressions):
            raise ValueError("output names must be unique")
        nodes: list[CircuitNode] = []
        ids: dict[tuple, str] = {}

        def visit(item: Expr) -> str:
            key = item.structural_key
            if key in ids:
                return ids[key]
            child_ids = tuple(visit(child) for child in item.args)
            node_id = f"n{len(nodes)}"
            if item.op == "VAR" and (item.value is None or not 0 <= item.value < input_count):
                raise ValueError(f"expression references invalid input index: {item.value}")
            nodes.append(CircuitNode(node_id, item.op, child_ids, item.value))
            ids[key] = node_id
            return node_id

        outputs = tuple((name, visit(expr)) for name, expr in expressions.items())
        return cls(input_count, tuple(nodes), outputs)

    def _evaluate_nodes(self, assignment: tuple[int, ...]) -> dict[str, int]:
        assignment_to_row(assignment, self.input_count)
        values: dict[str, int] = {}
        for node in self.nodes:
            if node.op == "VAR":
                assert node.value is not None
                values[node.node_id] = int(bool(assignment[node.value]))
            elif node.op == "CONST":
                values[node.node_id] = int(bool(node.value))
            else:
                values[node.node_id] = apply_gate(
                    node.op, tuple(values[source] for source in node.inputs), 1
                )
        return values

    def evaluate(self, assignment: tuple[int, ...] | list[int]) -> dict[str, int]:
        values = self._evaluate_nodes(tuple(assignment))
        return {name: values[node_id] for name, node_id in self.outputs}

    def truth_tables(self) -> dict[str, TruthTable]:
        bits = {name: 0 for name, _ in self.outputs}
        for row, assignment in enumerate(product((0, 1), repeat=self.input_count)):
            values = self._evaluate_nodes(assignment)
            for name, node_id in self.outputs:
                bits[name] |= values[node_id] << row
        return {name: TruthTable(self.input_count, value) for name, value in bits.items()}

    def verify(self, expected: Mapping[str, TruthTable]) -> bool:
        actual = self.truth_tables()
        if set(actual) != set(expected):
            return False
        return all(actual[name] == table for name, table in expected.items())

    def fanout(self) -> dict[str, int]:
        counts = {node.node_id: 0 for node in self.nodes}
        for node in self.nodes:
            for source in node.inputs:
                counts[source] += 1
        for _, source in self.outputs:
            counts[source] += 1
        return counts

    def metrics(self) -> NetworkMetrics:
        depths: dict[str, int] = {}
        for node in self.nodes:
            depths[node.node_id] = (
                0 if node.op in {"VAR", "CONST"}
                else 1 + max(depths[source] for source in node.inputs)
            )
        fanout = self.fanout()
        tables = self.truth_tables()
        densities = tuple(
            (name, sum(table.outputs()) / len(table))
            for name, table in sorted(tables.items())
        )
        return NetworkMetrics(
            unique_gate_count=sum(node.op in GATE_LIBRARY for node in self.nodes),
            logic_depth=max((depths[node_id] for _, node_id in self.outputs), default=0),
            max_fanout=max(fanout.values(), default=0),
            input_fanout=tuple(
                next((fanout[node.node_id] for node in self.nodes if node.op == "VAR" and node.value == i), 0)
                for i in range(self.input_count)
            ),
            output_one_density=densities,
        )

    def to_dict(self) -> dict:
        return {
            "input_count": self.input_count,
            "nodes": [
                {"id": node.node_id, "op": node.op, "inputs": list(node.inputs), "value": node.value}
                for node in self.nodes
            ],
            "outputs": {name: node_id for name, node_id in self.outputs},
            "truth_tables": {name: table.hex() for name, table in self.truth_tables().items()},
            "metrics": {
                "unique_gate_count": self.metrics().unique_gate_count,
                "logic_depth": self.metrics().logic_depth,
                "max_fanout": self.metrics().max_fanout,
                "input_fanout": list(self.metrics().input_fanout),
            },
        }
