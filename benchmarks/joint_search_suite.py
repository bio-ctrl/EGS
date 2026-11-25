"""Deterministic multi-case benchmark suite for joint multi-output search.

Every case is reported, including cases where joint search does not improve
on the selected-expression baseline. Structural metrics are not PPA claims.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orcus.joint_search import JointSearchConfig, search_multi_output_joint
from orcus.multioutput import synthesize_multi_output
from orcus.synthesis import SynthesisConfig
from orcus.truth_table import TruthTable


def table(fn):
    return TruthTable.from_callable(3, fn)


def benchmark_cases():
    # Deliberately mix sharing-friendly, arithmetic, selection, and unrelated
    # outputs. The suite is fixed in source so results are reproducible.
    return {
        "shared_product": {
            "ab": table(lambda a, b, c: a & b),
            "ab_or_c": table(lambda a, b, c: (a & b) | c),
            "ab_xor_c": table(lambda a, b, c: (a & b) ^ c),
        },
        "full_adder": {
            "sum": table(lambda a, b, c: a ^ b ^ c),
            "carry": table(lambda a, b, c: int(a + b + c >= 2)),
        },
        "dual_mux": {
            "mux_bc": table(lambda s, b, c: b if s else c),
            "mux_cb": table(lambda s, b, c: c if s else b),
        },
        "parity_and_majority": {
            "parity": table(lambda a, b, c: a ^ b ^ c),
            "majority": table(lambda a, b, c: int(a + b + c >= 2)),
            "all_three": table(lambda a, b, c: a & b & c),
        },
        "two_bit_decoder": {
            "m0": table(lambda a, b, c: int((a, b) == (0, 0))),
            "m3": table(lambda a, b, c: int((a, b) == (0, 1))),
            "m5": table(lambda a, b, c: int((a, b) == (1, 0))),
            "m7": table(lambda a, b, c: int((a, b) == (1, 1))),
        },
    }


def run_case(name, targets, synthesis, generated_limit, combination_limit):
    start = perf_counter()
    baseline = synthesize_multi_output(targets, synthesis)
    baseline_seconds = perf_counter() - start

    config = JointSearchConfig(
        synthesis=synthesis,
        max_generated_expressions=generated_limit,
        max_combinations=combination_limit,
    )
    start = perf_counter()
    joint = search_multi_output_joint(targets, config)
    joint_seconds = perf_counter() - start

    if not baseline.found or baseline.network is None:
        raise RuntimeError(f"{name}: baseline failed to synthesize all outputs")
    if not joint.found or joint.network is None:
        raise RuntimeError(f"{name}: joint search failed: {joint.missing_outputs}")
    baseline_verified = baseline.network.verify(targets)
    joint_verified = joint.network.verify(targets)
    if not baseline_verified or not joint_verified:
        raise RuntimeError(f"{name}: exhaustive functional verification failed")

    baseline_gates = baseline.shared_gate_count
    joint_gates = joint.joint_gate_count
    return {
        "case": name,
        "outputs": list(targets),
        "output_count": len(targets),
        "baseline": {
            "independent_gate_count": baseline.independent_gate_count,
            "shared_unique_gate_count": baseline_gates,
            "logic_depth": baseline.metrics.logic_depth,
            "max_fanout": baseline.metrics.max_fanout,
            "elapsed_seconds": baseline_seconds,
            "verified": baseline_verified,
        },
        "joint_search": {
            "unique_gate_count": joint_gates,
            "logic_depth": joint.metrics.logic_depth,
            "max_fanout": joint.metrics.max_fanout,
            "candidates_per_output": dict(joint.candidates_per_output),
            "generated_expressions": joint.generated_expressions,
            "combinations_evaluated": joint.combinations_evaluated,
            "search_truncated": joint.search_truncated,
            "elapsed_seconds": joint_seconds,
            "verified": joint_verified,
            "network": joint.network.to_dict(),
        },
        "comparison": {
            "gate_delta_baseline_minus_joint": baseline_gates - joint_gates,
            "improved_gate_count": joint_gates < baseline_gates,
            "interpretation": (
                "Positive delta means fewer structural DAG gates in this case; "
                "it is not mapped area, timing, power, or silicon evidence."
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-gates", type=int, default=3)
    parser.add_argument("--max-generated-expressions", type=int, default=100_000)
    parser.add_argument("--max-combinations", type=int, default=50_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    synthesis = SynthesisConfig(input_count=3, max_gates=args.max_gates)
    results = [
        run_case(name, targets, synthesis, args.max_generated_expressions, args.max_combinations)
        for name, targets in benchmark_cases().items()
    ]
    record = {
        "experiment_id": "joint-multioutput-suite-v1",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "input_count": 3,
        "gate_library": list(synthesis.gates),
        "max_gates_per_expression": args.max_gates,
        "limits": {
            "max_generated_expressions": args.max_generated_expressions,
            "max_combinations": args.max_combinations,
        },
        "summary": {
            "cases": len(results),
            "cases_improved": sum(item["comparison"]["improved_gate_count"] for item in results),
            "cases_equal": sum(item["comparison"]["gate_delta_baseline_minus_joint"] == 0 for item in results),
            "cases_regressed": sum(item["comparison"]["gate_delta_baseline_minus_joint"] < 0 for item in results),
            "all_baseline_verified": all(item["baseline"]["verified"] for item in results),
            "all_joint_verified": all(item["joint_search"]["verified"] for item in results),
            "any_search_truncated": any(item["joint_search"]["search_truncated"] for item in results),
        },
        "results": results,
        "claims_boundary": (
            "This suite compares two technology-independent structural search "
            "methods on five small synthetic three-input cases. It does not "
            "establish superiority over commercial EDA, mapped PPA, novelty, "
            "or physical hardware performance."
        ),
    }
    rendered = json.dumps(record, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
