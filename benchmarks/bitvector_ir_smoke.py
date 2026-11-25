"""Smoke benchmark for the typed bit-vector dataflow IR."""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orcus.bitvector import BitVectorGraph, DataNode, DataOutput, DataPort


def main() -> int:
    adder = BitVectorGraph(
        inputs=(DataPort("a", 8), DataPort("b", 8)),
        nodes=(DataNode("sum9", "add", ("a", "b"), 9),),
        outputs=(DataOutput("sum", "sum9", 9),),
    )
    mux = BitVectorGraph(
        inputs=(DataPort("sel", 1), DataPort("a", 4), DataPort("b", 4)),
        nodes=(DataNode("chosen", "mux", ("sel", "a", "b"), 4),),
        outputs=(DataOutput("out", "chosen", 4),),
    )
    reports = {
        "adder_8bit": adder.verify_exhaustive(lambda x: {"sum": x["a"] + x["b"]}),
        "mux_4bit": mux.verify_exhaustive(lambda x: {"out": x["a"] if x["sel"] else x["b"]}),
    }
    result = {
        "experiment": "typed-bitvector-ir-smoke-v1",
        "cases": {
            name: {
                "passed": report.passed,
                "exhaustive": report.exhaustive,
                "vectors_checked": report.vectors_checked,
                "input_bits": report.input_bits,
            }
            for name, report in reports.items()
        },
        "metrics": {
            "adder_8bit": {
                "operation_count": adder.metrics().operation_count,
                "logic_depth": adder.metrics().logic_depth,
                "max_fanout": adder.metrics().max_fanout,
            },
            "mux_4bit": {
                "operation_count": mux.metrics().operation_count,
                "logic_depth": mux.metrics().logic_depth,
                "max_fanout": mux.metrics().max_fanout,
            },
        },
        "limitations": [
            "This validates the IR and evaluator, not architecture-search quality.",
            "Structural metrics are not mapped or physical PPA.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(report.passed and report.exhaustive for report in reports.values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
