"""Deterministic enumerative synthesis baseline for small Boolean functions.

The engine searches expression trees in increasing gate count. For pure
combinational Boolean logic, a higher-cost implementation of the same
single-output truth table is dominated by its lower-cost implementation for
this tree-cost objective. Shared multi-output DAG optimization is intentionally
not claimed by this baseline and is a later research direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from .circuit import Circuit, CircuitMetrics, measure_circuit
from .expression import Expr, constant, gate, variable
from .gates import DEFAULT_GATES, GATE_LIBRARY
from .truth_table import TruthTable


@dataclass(frozen=True, slots=True)
class SynthesisConfig:
    max_gates: int = 7
    gates: tuple[str, ...] = DEFAULT_GATES
    input_count: int = 3

    def __post_init__(self) -> None:
        if self.max_gates < 0:
            raise ValueError("max_gates must be non-negative")
        if not 1 <= self.input_count <= 3:
            raise ValueError("the enumerative baseline currently supports 1 to 3 inputs")
        if not self.gates:
            raise ValueError("at least one gate must be enabled")
        unknown = set(self.gates) - set(GATE_LIBRARY)
        if unknown:
            raise ValueError(f"unknown gates: {sorted(unknown)}")


@dataclass(frozen=True, slots=True)
class SynthesisResult:
    target: TruthTable
    found: bool
    circuit: Circuit | None
    metrics: CircuitMetrics | None
    elapsed_seconds: float
    search_depth: int
    explored_functions: int
    expression: str | None

    def to_dict(self) -> dict:
        return {
            "target": self.target.hex(),
            "target_rows": self.target.binary(),
            "found": self.found,
            "elapsed_seconds": self.elapsed_seconds,
            "search_depth": self.search_depth,
            "explored_functions": self.explored_functions,
            "expression": self.expression,
            "metrics": None if self.metrics is None else {
                "gate_count": self.metrics.gate_count,
                "logic_depth": self.metrics.logic_depth,
                "max_fanout": self.metrics.max_fanout,
                "input_fanout": list(self.metrics.input_fanout),
                "output_one_density": self.metrics.output_one_density,
                "output_toggle_proxy": self.metrics.output_toggle_proxy,
            },
            "circuit": None if self.circuit is None else self.circuit.to_dict(),
        }


class SynthesisEngine:
    def __init__(self, config: SynthesisConfig | None = None) -> None:
        self.config = config or SynthesisConfig()
        self._known: dict[int, Expr] = {}
        self._by_cost: list[list[Expr]] = []
        self._enumerated_to = -1
        self._initialize()

    def _initialize(self) -> None:
        n = self.config.input_count
        row_count = 1 << n
        mask = (1 << row_count) - 1
        seeds = [constant(False, 0, n), constant(True, mask, n)]
        seeds.extend(variable(i, TruthTable.variable(n, i).bits) for i in range(n))
        unique: dict[int, Expr] = {}
        for expr in seeds:
            current = unique.get(expr.truth)
            if current is None or expr.structural_key < current.structural_key:
                unique[expr.truth] = expr
        self._known = unique
        self._by_cost = [sorted(unique.values(), key=lambda e: (e.truth, e.structural_key))]
        self._enumerated_to = 0

    @staticmethod
    def _rank(expr: Expr) -> tuple:
        return (expr.depth, expr.structural_key)

    def _enumerate_one_cost(self, cost: int) -> None:
        mask = (1 << (1 << self.config.input_count)) - 1
        candidates: dict[int, Expr] = {}
        enabled = [GATE_LIBRARY[name] for name in self.config.gates]

        for spec in enabled:
            if spec.arity == 1 and cost >= 1:
                child_cost = cost - 1
                if child_cost < len(self._by_cost):
                    for child in self._by_cost[child_cost]:
                        expr = gate(spec.name, (child,), mask)
                        if expr.truth in self._known:
                            continue
                        prior = candidates.get(expr.truth)
                        if prior is None or self._rank(expr) < self._rank(prior):
                            candidates[expr.truth] = expr

            elif spec.arity == 2:
                total_child_cost = cost - 1
                for left_cost in range(total_child_cost // 2 + 1):
                    right_cost = total_child_cost - left_cost
                    if right_cost >= len(self._by_cost):
                        continue
                    if left_cost >= len(self._by_cost):
                        continue
                    left_group = self._by_cost[left_cost]
                    right_group = self._by_cost[right_cost]
                    if left_cost == right_cost:
                        pairs = (
                            (left_group[i], left_group[j])
                            for i in range(len(left_group))
                            for j in range(i, len(left_group))
                        )
                    else:
                        pairs = (
                            (left, right)
                            for left in left_group
                            for right in right_group
                        )
                    for left, right in pairs:
                        expr = gate(spec.name, (left, right), mask)
                        if expr.truth in self._known:
                            continue
                        prior = candidates.get(expr.truth)
                        if prior is None or self._rank(expr) < self._rank(prior):
                            candidates[expr.truth] = expr

        fresh = sorted(candidates.values(), key=lambda e: (e.truth, self._rank(e)))
        for expr in fresh:
            self._known[expr.truth] = expr
        self._by_cost.append(fresh)
        self._enumerated_to = cost

    def enumerate(self, max_gates: int | None = None) -> dict[int, Expr]:
        limit = self.config.max_gates if max_gates is None else max_gates
        if limit < 0:
            raise ValueError("max_gates must be non-negative")
        if limit > self.config.max_gates:
            raise ValueError("requested limit exceeds configured max_gates")
        while self._enumerated_to < limit:
            self._enumerate_one_cost(self._enumerated_to + 1)
        return {truth: expr for truth, expr in self._known.items() if expr.gate_count <= limit}

    def synthesize(self, target: TruthTable) -> SynthesisResult:
        if target.input_count != self.config.input_count:
            raise ValueError(
                f"target has {target.input_count} inputs; engine is configured for {self.config.input_count}"
            )
        started = perf_counter()
        self.enumerate()
        elapsed = perf_counter() - started
        expr = self._known.get(target.bits)
        if expr is None:
            return SynthesisResult(
                target, False, None, None, elapsed, self._enumerated_to,
                len(self._known), None,
            )
        circuit = Circuit.from_expression(expr, self.config.input_count)
        return SynthesisResult(
            target=target,
            found=circuit.verify(target),
            circuit=circuit,
            metrics=measure_circuit(circuit),
            elapsed_seconds=elapsed,
            search_depth=expr.gate_count,
            explored_functions=len(self._known),
            expression=expr.render(),
        )
