"""Command-line entry point for ORCUS baseline experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .experiment import run_standard_suite, write_jsonl
from .synthesis import SynthesisConfig, SynthesisEngine
from .targets import benchmark_targets
from .verilog import emit_verilog


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orcus", description="ORCUS Boolean architecture exploration baseline")
    sub = parser.add_subparsers(dest="command", required=True)
    synth = sub.add_parser("synthesize", help="synthesize a named three-input target")
    synth.add_argument("target", choices=sorted(benchmark_targets()))
    synth.add_argument("--max-gates", type=int, default=7)
    synth.add_argument("--verilog", type=Path)
    suite = sub.add_parser("benchmark", help="run the standard target suite")
    suite.add_argument("--max-gates", type=int, default=7)
    suite.add_argument("--output", type=Path, default=Path("artifacts/baseline.jsonl"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "synthesize":
        target = benchmark_targets()[args.target]
        result = SynthesisEngine(SynthesisConfig(max_gates=args.max_gates)).synthesize(target)
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        if args.verilog and result.circuit:
            args.verilog.parent.mkdir(parents=True, exist_ok=True)
            args.verilog.write_text(emit_verilog(result.circuit), encoding="utf-8")
        return 0 if result.found else 2
    records = run_standard_suite(args.max_gates)
    write_jsonl(records, args.output)
    print(json.dumps(records, indent=2, sort_keys=True))
    return 0 if all(row["verified"] for row in records) else 2


if __name__ == "__main__":
    raise SystemExit(main())
