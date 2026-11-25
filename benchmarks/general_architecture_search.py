"""Benchmark generic associative dataflow topology search against Yosys."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.adder_architecture_suite import yosys_cells
from orcus.architecture_search import run_search


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", choices=["add", "and", "or", "xor"], default="add")
    parser.add_argument("--operands", type=int, default=5)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--max-candidates", type=int, default=2000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-yosys", action="store_true")
    args = parser.parse_args()

    binary = shutil.which("yosys")
    if args.require_yosys and not binary:
        raise RuntimeError("Yosys is required but not installed")
    report = run_search(args.operator, args.operands, args.width, args.max_candidates)

    if binary:
        for candidate in report["candidates"]:
            module = candidate["name"]
            candidate["yosys"] = yosys_cells(candidate["verilog"], module, binary)

    result = {
        "experiment": "orcus-general-associative-architecture-search-v1",
        "yosys_available": bool(binary),
        "result": report,
        "interpretation_limits": [
            "The generator searches associative/commutative binary-tree topologies only.",
            "This is not unrestricted architecture invention or a claim of novelty.",
            "The current benchmark is a small five-input, two-bit synthetic workload.",
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
