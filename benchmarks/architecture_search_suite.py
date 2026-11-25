"""Run deterministic architecture search and independent Yosys synthesis."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orcus.adder_search import search_report
from benchmarks.adder_architecture_suite import yosys_cells


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--widths", nargs="+", type=int, default=[4, 8, 16, 32])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-yosys", action="store_true")
    args = parser.parse_args()
    binary = shutil.which("yosys")
    if args.require_yosys and not binary:
        raise RuntimeError("Yosys is required but not installed")

    reports = []
    for width in args.widths:
        report = search_report(width)
        if binary:
            for candidate in report["candidates"]:
                module = f"orcus_{candidate['name']}_{width}"
                candidate["yosys"] = yosys_cells(candidate["verilog"], module, binary)
        reports.append(report)

    result = {
        "experiment": "orcus-architecture-search-v1",
        "yosys_available": bool(binary),
        "results": reports,
        "limitations": [
            "Search enumerates three known adder families; it does not invent arbitrary circuits.",
            "Pareto optimality applies only to this generated candidate set and three structural metrics.",
            "Widths above eight use deterministic bounded sampling, not exhaustive equivalence proof.",
            "Yosys generic-cell counts are not mapped standard-cell or physical PPA.",
        ],
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
