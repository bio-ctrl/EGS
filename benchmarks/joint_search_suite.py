"""Deterministic multi-case benchmark suite for joint multi-output search.

Every case is reported, including cases where joint search does not improve
on the selected-expression baseline. Structural metrics are not PPA claims.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orcus.joint_search import JointSearchConfig, search_multi_output_joint
from orcus.multioutput import synthesize_multi_output
from orcus.synthesis import SynthesisConfig
from orcus.truth_table import TruthTable
from orcus.network_verilog import emit_network_verilog


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
        "half_adder": {
            "sum": table(lambda a, b, c: a ^ b),
            "carry": table(lambda a, b, c: a & b),
        },
        "dual_mux": {
            "mux_bc": table(lambda s, b, c: b if s else c),
            "mux_cb": table(lambda s, b, c: c if s else b),
        },
        "parity_and_or": {
            "parity": table(lambda a, b, c: a ^ b ^ c),
            "at_least_one": table(lambda a, b, c: int(bool(a or b or c))),
            "all_three": table(lambda a, b, c: a & b & c),
        },
        "two_bit_decoder": {
            "m0": table(lambda a, b, c: int((a, b) == (0, 0))),
            "m3": table(lambda a, b, c: int((a, b) == (0, 1))),
            "m5": table(lambda a, b, c: int((a, b) == (1, 0))),
            "m7": table(lambda a, b, c: int((a, b) == (1, 1))),
        },
    }


def yosys_stats(network, module_name, yosys_binary):
    """Synthesize one emitted network with Yosys and return generic cell stats."""
    source = emit_network_verilog(network, module_name=module_name)
    with tempfile.TemporaryDirectory(prefix="orcus-yosys-") as directory:
        verilog_path = Path(directory) / f"{module_name}.v"
        verilog_path.write_text(source, encoding="utf-8")
        command = (
            f"read_verilog {verilog_path}; hierarchy -top {module_name}; "
            f"synth -top {module_name}; stat"
        )
        completed = subprocess.run(
            [yosys_binary, "-p", command], check=True, capture_output=True, text=True
        )
        matches = re.findall(r"Number of cells:\s+(\d+)", completed.stdout)
        if not matches:
            raise RuntimeError(f"could not parse Yosys cell count for {module_name}")
        version = subprocess.run(
            [yosys_binary, "-V"], check=True, capture_output=True, text=True
        ).stdout.strip()
        return {
            "generic_cell_count": int(matches[-1]),
            "yosys_version": version,
            "flow": "read_verilog; hierarchy; synth; stat",
            "library": "Yosys generic internal cells; no foundry standard-cell library",
        }


def run_case(name, targets, synthesis, generated_limit, combination_limit, yosys_binary=None):
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
    external = None
    if yosys_binary:
        external = {
            "baseline": yosys_stats(baseline.network, f"orcus_base_{name}", yosys_binary),
            "joint_search": yosys_stats(joint.network, f"orcus_joint_{name}", yosys_binary),
        }
        external["generic_cell_delta_baseline_minus_joint"] = (
            external["baseline"]["generic_cell_count"]
            - external["joint_search"]["generic_cell_count"]
        )

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
        "yosys_comparison": external,
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
    parser.add_argument("--require-yosys", action="store_true")
    args = parser.parse_args()

    yosys_binary = shutil.which("yosys")
    if args.require_yosys and not yosys_binary:
        raise RuntimeError("--require-yosys was set but yosys is not installed")

    synthesis = SynthesisConfig(input_count=3, max_gates=args.max_gates)
    results = [
        run_case(
            name, targets, synthesis, args.max_generated_expressions,
            args.max_combinations, yosys_binary
        )
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
        "external_synthesis": {
            "tool": "Yosys",
            "available": bool(yosys_binary),
            "version": (
                subprocess.run([yosys_binary, "-V"], check=True, capture_output=True, text=True).stdout.strip()
                if yosys_binary else None
            ),
            "scope": "generic-cell synthesis only; not mapped to a foundry library",
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
