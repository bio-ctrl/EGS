# ORCUS

**Optimized Representation & Computational Understanding System**

ORCUS is an experimental autonomous computational-architecture discovery
project. Its first deliverable is a reproducible Boolean-circuit search engine
that establishes a transparent baseline before more ambitious search methods
are introduced.

> Status: research prototype, v0.1.0. This is not a production synthesizer and
> does not make claims about physical silicon performance or algorithmic
> novelty.

## What is implemented

- Packed truth tables for small combinational Boolean functions.
- A configurable primitive gate library: NOT, AND, OR, XOR, NAND, NOR, XNOR.
- Deterministic enumerative expression-tree synthesis in increasing gate count.
- A circuit IR with structural common-subexpression deduplication.
- A multi-output DAG network representation that shares repeated logic across outputs.
- Multi-output truth-table verification and Verilog emission.
- Exhaustive functional verification for every input assignment.
- Gate-count, logic-depth, fanout, and explicitly limited switching-proxy
  metrics.
- Verilog emission for inspection and downstream synthesis experiments.
- A reproducible benchmark harness and JSON Lines result records.
- A five-case multi-output joint-search suite with exhaustive verification.
- Bit-level ripple-carry and Kogge–Stone adder architecture generators with Verilog export and structural metrics.
- A typed, width-aware dataflow IR for multi-bit arithmetic, bitwise logic, muxes, comparisons, and shifts, with exhaustive verification and Verilog export.
- A deterministic architecture-search experiment that generates ripple, Sklansky, and Kogge–Stone adders, verifies them, and computes a multi-objective Pareto frontier.
- Optional Yosys generic-cell synthesis comparison for baseline and joint candidates.
- Unit tests and a GitHub Actions workflow.

## Quick start

Requires Python 3.11 or newer. The core project has no third-party runtime
dependencies.

```bash
python -m unittest discover -s tests -v
python -m orcus synthesize parity3 --max-gates 7
python -m orcus synthesize majority3 --max-gates 7 --verilog artifacts/majority3.v
python -m orcus benchmark --max-gates 7 --output artifacts/baseline.jsonl
python benchmarks/joint_search_suite.py --max-gates 3 --output artifacts/joint-suite.json
python benchmarks/bitvector_ir_smoke.py
python benchmarks/architecture_search_suite.py --widths 4 8 16 32 --require-yosys --output artifacts/architecture-search.json
```

Install as a local CLI if desired:

```bash
python -m pip install -e .
orcus synthesize mux3 --max-gates 7
```

## Search model

The initial engine enumerates single-output expression trees by increasing
primitive-gate count. It packs each Boolean function into an integer whose bit
positions correspond to input assignments in lexicographic order. For three
inputs, all eight input rows fit in one byte. Each gate applies bit-parallel
operations to these truth-table integers.

A lower-gate implementation of the same truth table dominates a higher-gate
implementation for the current tree-cost objective. The engine retains one
minimum-gate representative per truth function and breaks equal-cost ties by
logic depth and deterministic structural order. This gives a transparent
baseline for small functions; it is not a complete account of technology-aware
logic synthesis.

## Metrics and limitations

`gate_count` counts unique gate nodes in the compiled IR. `logic_depth` is the
longest gate path. `max_fanout` and `input_fanout` are structural counts.
`output_toggle_proxy` is an output activity proxy under uniform,
independent input vectors, not a power estimate.

For three inputs, the configured library reaches all 256 Boolean truth tables within the enumerated search bound; the exhaustive test suite verifies each emitted circuit against every input row. The current implementation does not model a standard-cell library, gate drive
strength, area, delay, capacitance, fanout buffering, routing, placement,
clocking, hazards, or manufacturing constraints. No claim about real silicon
PPA should be drawn from these metrics.

## Project map

```text
orcus/                 Core package
  truth_table.py       Truth-table encoding and bit-parallel operations
  gates.py             Primitive gate library
  expression.py        Immutable expression representation
  synthesis.py         Deterministic enumerative search
  circuit.py           Single-output circuit IR and structural metrics
  network.py           Multi-output DAG representation and validation
  network_verilog.py   Multi-output Verilog emitter
  verilog.py           Verilog emitter
  targets.py           Canonical benchmark functions
  experiment.py        Reproducible experiment records
  cli.py               Command-line interface
tests/                 Unit and functional-verification tests
examples/              Small usage example
benchmarks/            Baseline and multi-output research runners
docs/                  Research plan and experimental protocol
.github/workflows/     Continuous-integration test workflow
```

## Next research milestones

1. Add a search procedure that directly optimizes multi-output DAGs instead of only compiling shared expressions.
2. Introduce Pareto search over gate count, depth, fanout, and activity.
3. Expand benchmark coverage and compare against independent synthesis tools (the initial Yosys generic-cell check is not foundry PPA).
4. Export and map Verilog against a documented cell library.
5. Compare generated arithmetic architectures (ripple-carry and parallel-prefix) with exhaustive small-width verification and independent Yosys generic-cell synthesis.
6. Only then investigate physical PPA and FPGA validation.

See [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md),
[docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md), and the
[first five-case joint-search results](docs/JOINT_SEARCH_RESULTS.md).
