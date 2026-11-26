"""Bounded joint search over alternative multi-output Boolean implementations.

Unlike the structural-sharing baseline, this module retains multiple
implementations per truth table and evaluates combinations as shared DAGs.
The search is deliberately bounded and reports when limits truncate exploration.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement, product
from typing import Mapping

from .expression import Expr, constant, gate, variable
from .gates import GATE_LIBRARY
from .network import CircuitNetwork, NetworkMetrics
from .synthesis import SynthesisConfig, SynthesisEngine
from .truth_table import TruthTable


@dataclass(frozen=True, slots=True)
class JointSearchConfig:
    synthesis: SynthesisConfig = SynthesisConfig(max_gates=3)
    candidates_per_truth_per_cost: int = 4
    max_generated_expressions: int = 100_000
    max_combinations: int = 50_000

    def __post_init__(self) -> None:
        if self.candidates_per_truth_per_cost < 1:
            raise ValueError("candidates_per_truth_per_cost must be positive")
        if self.max_generated_expressions < 1:
            raise ValueError("max_generated_expressions must be positive")
        if self.max_combinations < 1:
            raise ValueError("max_combinations must be positive")


@dataclass(frozen=True, slots=True)
class JointSearchResult:
    found: bool
    network: CircuitNetwork | None
    metrics: NetworkMetrics | None
    independent_gate_count: int | None
    joint_gate_count: int | None
    gates_saved: int | None
    candidates_per_output: tuple[tuple[str, int], ...]
    combinations_evaluated: int
    generated_expressions: int
    search_truncated: bool
    missing_outputs: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "found": self.found,
            "independent_gate_count": self.independent_gate_count,
            "joint_gate_count": self.joint_gate_count,
            "gates_saved": self.gates_saved,
            "candidates_per_output": dict(self.candidates_per_output),
            "combinations_evaluated": self.combinations_evaluated,
            "generated_expressions": self.generated_expressions,
            "search_truncated": self.search_truncated,
            "missing_outputs": list(self.missing_outputs),
            "network": None if self.network is None else self.network.to_dict(),
        }


def _rank(expr: Expr) -> tuple:
    return (expr.depth, expr.structural_key)


def _candidate_catalogue(config: JointSearchConfig) -> tuple[dict[int, list[Expr]], int, bool]:
    synthesis = config.synthesis
    n = synthesis.input_count
    if not 1 <= n <= 3:
        raise ValueError("joint expression search currently supports 1 to 3 inputs")
    row_count = 1 << n
    mask = (1 << row_count) - 1

    seeds = [constant(False, 0, n), constant(True, mask, n)]
    seeds.extend(variable(i, TruthTable.variable(n, i).bits) for i in range(n))
    seed_by_truth: dict[int, Expr] = {}
    for expr in seeds:
        previous = seed_by_truth.get(expr.truth)
        if previous is None or expr.structural_key < previous.structural_key:
            seed_by_truth[expr.truth] = expr

    layers: list[list[Expr]] = [
        sorted(seed_by_truth.values(), key=lambda item: (item.truth, _rank(item)))
    ]
    catalogue: dict[int, list[Expr]] = {
        truth: [expr] for truth, expr in seed_by_truth.items()
    }
    generated = 0
    truncated = False
    enabled = [GATE_LIBRARY[name] for name in synthesis.gates]

    for cost in range(1, synthesis.max_gates + 1):
        buckets: dict[int, dict[tuple, Expr]] = {}

        def retain(expr: Expr) -> bool:
            nonlocal generated, truncated
            generated += 1
            if generated > config.max_generated_expressions:
                truncated = True
                return False
            bucket = buckets.setdefault(expr.truth, {})
            key = expr.structural_key
            if key in bucket:
                return True
            bucket[key] = expr
            limit = config.candidates_per_truth_per_cost
            if len(bucket) > limit:
                worst_key, _ = max(bucket.items(), key=lambda item: _rank(item[1]))
                del bucket[worst_key]
                truncated = True
            return True

        stop_layer = False
        for spec in enabled:
            if spec.arity == 1:
                child_cost = cost - 1
                if child_cost < len(layers):
                    for child in layers[child_cost]:
                        if not retain(gate(spec.name, (child,), mask)):
                            stop_layer = True
                            break
            else:
                total_child_cost = cost - 1
                for left_cost in range(total_child_cost // 2 + 1):
                    right_cost = total_child_cost - left_cost
                    if right_cost >= len(layers) or left_cost >= len(layers):
                        continue
                    left_layer, right_layer = layers[left_cost], layers[right_cost]
                    pairs = (
                        combinations_with_replacement(left_layer, 2)
                        if left_cost == right_cost
                        else product(left_layer, right_layer)
                    )
                    for left, right in pairs:
                        if not retain(gate(spec.name, (left, right), mask)):
                            stop_layer = True
                            break
                    if stop_layer:
                        break
            if stop_layer:
                break

        layer = [
            expr
            for truth in sorted(buckets)
            for expr in sorted(buckets[truth].values(), key=_rank)
        ]
        layers.append(layer)
        for expr in layer:
            catalogue.setdefault(expr.truth, []).append(expr)
        if stop_layer:
            break

    for truth, expressions in catalogue.items():
        catalogue[truth] = sorted(
            expressions, key=lambda item: (item.gate_count, item.depth, item.structural_key)
        )
    return catalogue, generated, truncated


def search_multi_output_joint(
    targets: Mapping[str, TruthTable],
    config: JointSearchConfig | None = None,
) -> JointSearchResult:
    """Search bounded alternative implementations jointly across named outputs.

    The objective is lexicographic: unique shared gate count, network depth,
    maximum fanout, total expression-tree gate count, then deterministic order.
    This is exact over explored combinations, not a proof of global optimality.
    """
    if not targets:
        raise ValueError("at least one named output target is required")
    if any(not isinstance(name, str) or not name.strip() for name in targets):
        raise ValueError("output names must be non-empty strings")
    if any(not isinstance(table, TruthTable) for table in targets.values()):
        raise TypeError("all targets must be TruthTable instances")
    input_counts = {table.input_count for table in targets.values()}
    if len(input_counts) != 1:
        raise ValueError("all output truth tables must have the same input count")

    input_count = next(iter(input_counts))
    search_config = config or JointSearchConfig(
        synthesis=SynthesisConfig(input_count=input_count, max_gates=3)
    )
    if search_config.synthesis.input_count != input_count:
        raise ValueError("configuration input_count does not match target tables")

    catalogue, generated, truncated = _candidate_catalogue(search_config)
    candidate_sets: list[list[Expr]] = []
    counts: list[tuple[str, int]] = []
    missing: list[str] = []
    for name, target in targets.items():
        candidates = catalogue.get(target.bits, [])
        counts.append((name, len(candidates)))
        if not candidates:
            missing.append(name)
        candidate_sets.append(candidates)

    if missing:
        return JointSearchResult(
            False, None, None, None, None, None, tuple(counts), 0,
            generated, truncated, tuple(missing)
        )

    baseline_catalogue = SynthesisEngine(search_config.synthesis).enumerate()
    independent_gate_count = sum(
        baseline_catalogue[target.bits].gate_count for target in targets.values()
    )

    best_network = None
    best_metrics = None
    best_score = None
    combinations_evaluated = 0
    combination_truncated = False
    for combination in product(*candidate_sets):
        if combinations_evaluated >= search_config.max_combinations:
            combination_truncated = True
            break
        combinations_evaluated += 1
        expressions = {
            name: expr for name, expr in zip(targets.keys(), combination)
        }
        network = CircuitNetwork.from_expressions(expressions, input_count)
        if not network.verify(targets):
            raise AssertionError("joint candidate failed exhaustive truth-table verification")
        metrics = network.metrics()
        score = (
            metrics.unique_gate_count,
            metrics.logic_depth,
            metrics.max_fanout,
            sum(expr.gate_count for expr in combination),
            tuple(expr.structural_key for expr in combination),
        )
        if best_score is None or score < best_score:
            best_score = score
            best_network = network
            best_metrics = metrics

    if best_network is None or best_metrics is None:
        raise AssertionError("candidate product unexpectedly contained no combinations")

    joint_gate_count = best_metrics.unique_gate_count
    return JointSearchResult(
        True,
        best_network,
        best_metrics,
        independent_gate_count,
        joint_gate_count,
        independent_gate_count - joint_gate_count,
        tuple(counts),
        combinations_evaluated,
        generated,
        truncated or combination_truncated,
        (),
    )
