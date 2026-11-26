"""Multi-output synthesis baseline with explicit structural-sharing accounting.

This is deliberately a *baseline evaluator*, not a claim of globally optimal
multi-output synthesis. It reuses the deterministic single-output enumerator,
combines its selected expressions into a shared DAG, and compares unique DAG
gate count with the sum of independently synthesized gate counts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .network import CircuitNetwork, NetworkMetrics
from .synthesis import SynthesisConfig, SynthesisEngine
from .truth_table import TruthTable


@dataclass(frozen=True, slots=True)
class MultiOutputResult:
    found: bool
    network: CircuitNetwork | None
    metrics: NetworkMetrics | None
    independent_gate_count: int
    shared_gate_count: int | None
    gates_saved: int | None
    missing_outputs: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "found": self.found,
            "independent_gate_count": self.independent_gate_count,
            "shared_gate_count": self.shared_gate_count,
            "gates_saved": self.gates_saved,
            "missing_outputs": list(self.missing_outputs),
            "network": None if self.network is None else self.network.to_dict(),
        }


def synthesize_multi_output(
    targets: Mapping[str, TruthTable],
    config: SynthesisConfig | None = None,
) -> MultiOutputResult:
    """Synthesize named outputs and measure structural sharing in their DAG.

    The selected expression for each output is the deterministic minimum-gate
    expression found by the existing single-output enumerator. This function
    does not enumerate alternative expressions jointly, so its shared result
    is an upper bound for this particular selection, not a global optimum.
    """
    if not targets:
        raise ValueError("at least one named output target is required")
    if any(not isinstance(name, str) or not name.strip() for name in targets):
        raise ValueError("output names must be non-empty strings")
    input_counts = {table.input_count for table in targets.values()}
    if len(input_counts) != 1:
        raise ValueError("all output truth tables must have the same input count")

    input_count = next(iter(input_counts))
    base = config or SynthesisConfig(input_count=input_count)
    if base.input_count != input_count:
        raise ValueError("configuration input_count does not match target tables")

    engine = SynthesisEngine(base)
    catalogue = engine.enumerate()
    selected = {}
    independent_gate_count = 0
    missing = []

    for name, target in targets.items():
        expr = catalogue.get(target.bits)
        if expr is None:
            missing.append(name)
            continue
        selected[name] = expr
        independent_gate_count += expr.gate_count

    if missing:
        return MultiOutputResult(
            found=False,
            network=None,
            metrics=None,
            independent_gate_count=independent_gate_count,
            shared_gate_count=None,
            gates_saved=None,
            missing_outputs=tuple(missing),
        )

    network = CircuitNetwork.from_expressions(selected, input_count)
    if not network.verify(targets):
        raise AssertionError("combined multi-output network failed exhaustive verification")

    shared_gate_count = network.metrics().unique_gate_count
    return MultiOutputResult(
        found=True,
        network=network,
        metrics=network.metrics(),
        independent_gate_count=independent_gate_count,
        shared_gate_count=shared_gate_count,
        gates_saved=independent_gate_count - shared_gate_count,
        missing_outputs=(),
    )
