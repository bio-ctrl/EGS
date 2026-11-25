"""Compare ORCUS adder architecture families; optionally cross-check with Yosys."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orcus.adder_architectures import (
    build_kogge_stone_adder,
    build_ripple_carry_adder,
)


def yosys_cells(source: str, module: str, binary: str) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "candidate.v"
        path.write_text(source, encoding="utf-8")
        script = f"read_verilog {path}; hierarchy -top {module}; synth -top {module}; stat"
        run = subprocess.run([binary, "-p", script], capture_output=True, text=True, check=True)
        import re
        counts = re.findall(r"Number of cells:\s+(\d+)", run.stdout)
        if not counts:
            raise RuntimeError("could not parse Yosys generic cell count")
        return {"generic_cell_count": int(counts[-1]), "version": subprocess.run(
            [binary, "-V"], capture_output=True, text=True, check=True
        ).stdout.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--widths", nargs="+", type=int, default=[4, 8, 16, 32])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-yosys", action="store_true")
    args = parser.parse_args()
    binary = shutil.which("yosys")
    if args.require_yosys and not binary:
        raise RuntimeError("Yosys is required but not installed")
    rows = []
    for width in args.widths:
        ripple = build_ripple_carry_adder(width)
        prefix = build_kogge_stone_adder(width)
        limit = 1 << min(width, 8)
        for a in range(limit):
            for b in range(limit):
                if ripple.evaluate(a, b) != a + b or prefix.evaluate(a, b) != a + b:
                    raise AssertionError(f"functional verification failed at width={width}")
        row = {
            "width": width,
            "verification": {
                "exhaustive": width <= 8,
                "sampled_inputs_per_operand": limit if width > 8 else None,
                "passed": True,
            },
            "ripple": {
                "metrics": ripple.metrics().__dict__ if hasattr(ripple.metrics(), "__dict__") else {
                    "gate_count": ripple.metrics().gate_count,
                    "logic_depth": ripple.metrics().logic_depth,
                    "max_fanout": ripple.metrics().max_fanout,
                },
                "verilog": ripple.emit_verilog(),
            },
            "kogge_stone": {
                "metrics": {
                    "gate_count": prefix.metrics().gate_count,
                    "logic_depth": prefix.metrics().logic_depth,
                    "max_fanout": prefix.metrics().max_fanout,
                },
                "verilog": prefix.emit_verilog(),
            },
        }
        if binary:
            row["yosys"] = {
                "ripple": yosys_cells(ripple.emit_verilog(), f"orcus_ripple_{width}", binary),
                "kogge_stone": yosys_cells(prefix.emit_verilog(), f"orcus_kogge_stone_{width}", binary),
            }
        rows.append(row)
    result = {
        "experiment": "adder-architecture-family-v1",
        "tool": "ORCUS structural estimator",
        "yosys_available": bool(binary),
        "results": rows,
        "limitations": [
            "Structural gate count and depth are not physical area, timing, power, or energy.",
            "Yosys generic-cell counts are not mapped standard-cell PPA.",
            "Widths above eight use deterministic sampled functional checks, not exhaustive proof.",
            "No placement, routing, wire delay, or process-specific cell library is modeled.",
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
