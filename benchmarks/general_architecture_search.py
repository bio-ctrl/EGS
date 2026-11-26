"""Benchmark generic associative dataflow topology search against Yosys SAT/synthesis."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.adder_architecture_suite import yosys_cells
from orcus.architecture_search import run_search


def yosys_prove_equivalent(candidate_verilog: str, candidate_module: str,
                           operator: str, operands: int, width: int,
                           binary: str) -> dict:
    """Prove candidate == direct operator reference for every input assignment."""
    names = [f"x{i}" for i in range(operands)]
    port_list = ", ".join(names)
    declarations = "\n".join(
        f"  input [{width - 1}:0] {name};" for name in names
    )
    symbols = {"add": "+", "and": "&", "or": "|", "xor": "^"}
    reference_expression = f" {symbols[operator]} ".join(names)
    connections = ", ".join(f".{name}({name})" for name in names)
    reference = (
        f"module orcus_reference({port_list}, result);\n"
        f"{declarations}\n"
        f"  output [{width - 1}:0] result;\n"
        f"  assign result = {reference_expression};\n"
        f"endmodule\n"
    )
    miter = (
        f"module orcus_miter({port_list}, mismatch);\n"
        f"{declarations}\n"
        f"  output mismatch;\n"
        f"  wire [{width - 1}:0] candidate_value;\n"
        f"  wire [{width - 1}:0] reference_value;\n"
        f"  {candidate_module} dut({connections}, .result(candidate_value));\n"
        f"  orcus_reference ref({connections}, .result(reference_value));\n"
        f"  assign mismatch = |(candidate_value ^ reference_value);\n"
        f"endmodule\n"
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        candidate_path = root / "candidate.v"
        reference_path = root / "reference_miter.v"
        candidate_path.write_text(candidate_verilog, encoding="utf-8")
        reference_path.write_text(reference + miter, encoding="utf-8")
        script = (
            f"read_verilog {candidate_path} {reference_path}; "
            "hierarchy -top orcus_miter; flatten; opt; "
            "sat -verify -prove mismatch 0"
        )
        subprocess.run(
            [binary, "-p", script], capture_output=True, text=True, check=True
        )
        version = subprocess.run(
            [binary, "-V"], capture_output=True, text=True, check=True
        ).stdout.strip()
    return {"proved": True, "method": "Yosys SAT miter", "version": version}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", choices=["add", "and", "or", "xor"], default="add")
    parser.add_argument("--operands", type=int, default=4)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--max-candidates", type=int, default=2000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-yosys", action="store_true")
    args = parser.parse_args()

    binary = shutil.which("yosys")
    if args.require_yosys and not binary:
        raise RuntimeError("Yosys is required but not installed")
    report = run_search(args.operator, args.operands, args.width, args.max_candidates)

    baseline = None
    if binary:
        for candidate in report["candidates"]:
            module = candidate["name"]
            candidate["formal_equivalence"] = yosys_prove_equivalent(
                candidate["verilog"], module, args.operator,
                args.operands, args.width, binary,
            )
            candidate["verification"]["passed"] = candidate["formal_equivalence"]["proved"]
            candidate["verification"]["method"] = candidate["formal_equivalence"]["method"]
            candidate["yosys"] = yosys_cells(candidate["verilog"], module, binary)

        names = [f"x{i}" for i in range(args.operands)]
        ports = ", ".join(names)
        declarations = "\n".join(
            f"  input [{args.width - 1}:0] {name};" for name in names
        )
        symbols = {"add": "+", "and": "&", "or": "|", "xor": "^"}
        expression = f" {symbols[args.operator]} ".join(names)
        baseline_source = (
            f"module orcus_reference_baseline({ports}, result);\n"
            f"{declarations}\n"
            f"  output [{args.width - 1}:0] result;\n"
            f"  assign result = {expression};\n"
            f"endmodule\n"
        )
        baseline = yosys_cells(
            baseline_source, "orcus_reference_baseline", binary
        )
        counts = [item["yosys"]["generic_cell_count"] for item in report["candidates"]]
        report["yosys_comparison"] = {
            "direct_expression_baseline_generic_cells": baseline["generic_cell_count"],
            "best_generated_candidate_generic_cells": min(counts),
            "worst_generated_candidate_generic_cells": max(counts),
            "generated_candidates_beating_baseline": sum(
                count < baseline["generic_cell_count"] for count in counts
            ),
            "generated_candidates_tying_baseline": sum(
                count == baseline["generic_cell_count"] for count in counts
            ),
            "generated_candidates_losing_to_baseline": sum(
                count > baseline["generic_cell_count"] for count in counts
            ),
        }

    result = {
        "experiment": "orcus-general-associative-architecture-search-v1",
        "yosys_available": bool(binary),
        "yosys_version": baseline["version"] if baseline else None,
        "direct_expression_baseline": baseline,
        "result": report,
        "interpretation_limits": [
            "The generator searches associative/commutative binary-tree topologies only.",
            "This is not unrestricted architecture invention or a claim of novelty.",
            "The current benchmark is a small four-input, two-bit synthetic workload.",
            "Yosys SAT proves combinational equivalence for the tested candidate/reference pairs.",
            "Yosys generic-cell counts are not mapped standard-cell area, delay, power, or physical PPA.",
        ],
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
