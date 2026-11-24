# ORCUS v0.1.0 validation report

## Environment

- Runtime: CPython 3.13.5
- Platform: Linux x86_64
- Runtime dependencies: Python standard library only
- Test command: `python -m unittest discover -s tests -v`
- Static bytecode compilation: `python -m compileall -q orcus tests examples benchmarks`

## Results

- Unit tests: **21 passed, 0 failed**.
- Three-input truth-function catalogue: **256 / 256 functions reached** within a four-gate expression-tree bound.
- Exhaustive checks: every catalogued function was compiled to the circuit IR and checked against all eight possible input assignments.
- Multi-output tests: shared subexpression construction, named-output evaluation, and output truth-table verification passed.
- CLI benchmark smoke test: majority3, parity3, and mux3 all synthesized and passed exhaustive verification.
- Verilog emitter tests: generated single-output and multi-output source structure passed static unit checks.

## Baseline candidates

| Target | Truth table | Unique gates | Logic depth | Exhaustively verified |
|---|---:|---:|---:|---|
| majority3 | `0xe8` | 4 | 3 | Yes |
| parity3 | `0x96` | 2 | 2 | Yes |
| mux3 (A selects B/C) | `0xca` | 3 | 3 | Yes |

The machine-readable, single-run records are in `artifacts/baseline.jsonl`. Search times in that file are smoke-test measurements from one run, not statistically robust performance claims.

## Not yet validated

- No external Verilog simulator or synthesis tool (`iverilog` / `yosys`) was available in the execution environment. Verilog emission has unit-level structural tests but has not been independently parsed, simulated, or synthesized by an HDL tool.
- No FPGA implementation, standard-cell mapping, placement, routing, timing closure, or physical power analysis has been performed.
- No comparison against ABC, Yosys, commercial synthesis, academic baselines, or patent/prior-art corpus has been completed.
- No claim of algorithmic novelty, silicon PPA improvement, patentability, or production readiness is supported by this baseline.

## Reproduction

From the repository root, with Python 3.11 or newer:

```bash
python -m unittest discover -s tests -v
python -m compileall -q orcus tests examples benchmarks
python -m orcus benchmark --max-gates 7 --output artifacts/baseline.jsonl
```
