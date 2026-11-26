"""Reproducible smoke benchmark for bounded joint multi-output search."""
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


def build_targets() -> dict[str, TruthTable]:
    return {
        "ab": TruthTable.from_callable(3, lambda a, b, c: a & b),
        "ab_or_c": TruthTable.from_callable(3, lambda a, b, c: (a & b) | c),
        "ab_xor_c": TruthTable.from_callable(3, lambda a, b, c: (a & b) ^ c),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-gates", type=int, default=3)
    parser.add_argument("--max-generated-expressions", type=int, default=100_000)
    parser.add_argument("--max-combinations", type=int, default=50_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    targets = build_targets()
    synthesis = SynthesisConfig(input_count=3, max_gates=args.max_gates)
    started = perf_counter()
    baseline = synthesize_multi_output(targets, synthesis)
    baseline_seconds = perf_counter() - started

    joint_config = JointSearchConfig(
        synthesis=synthesis,
        max_generated_expressions=args.max_generated_expressions,
        max_combinations=args.max_combinations,
    )
    started = perf_counter()
    joint = search_multi_output_joint(targets, joint_config)
    joint_seconds = perf_counter() - started

    if not baseline.found or baseline.network is None or not baseline.network.verify(targets):
        raise RuntimeError("baseline failed exhaustive verification")
    if not joint.found or joint.network is None or not joint.network.verify(targets):
        raise RuntimeError("joint search failed exhaustive verification")

    record = {
        "experiment_id": "joint-multioutput-smoke-v1",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "input_count": 3,
        "target_names": list(targets),
        "gate_library": list(synthesis.gates),
        "max_gates_per_expression": args.max_gates,
        "baseline": {
            "independent_gate_count": baseline.independent_gate_count,
            "shared_gate_count": baseline.shared_gate_count,
            "logic_depth": baseline.metrics.logic_depth,
            "elapsed_seconds": baseline_seconds,
            "verified": baseline.network.verify(targets),
        },
        "joint_search": {
            "unique_gate_count": joint.joint_gate_count,
            "logic_depth": joint.metrics.logic_depth,
            "max_fanout": joint.metrics.max_fanout,
            "candidates_per_output": dict(joint.candidates_per_output),
            "generated_expressions": joint.generated_expressions,
            "combinations_evaluated": joint.combinations_evaluated,
            "search_truncated": joint.search_truncated,
            "elapsed_seconds": joint_seconds,
            "verified": joint.network.verify(targets),
        },
        "comparison": {
            "gate_delta_vs_shared_baseline": baseline.shared_gate_count - joint.joint_gate_count,
            "interpretation": "Positive means fewer structural DAG gates in this benchmark only; it is not mapped PPA or silicon evidence.",
        },
    }
    rendered = json.dumps(record, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
