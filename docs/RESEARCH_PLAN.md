# ORCUS research plan

## Research objective

Investigate whether alternative search representations and cost models can find
useful combinational architectures that are missed or poorly exposed by
conventional expression-tree enumeration. The initial implementation is a
small, transparent baseline—not a claim of a new synthesis algorithm.

## Baseline scope (v0.1)

- Three-input single-output Boolean functions.
- Eight-row truth-table representation, packed into one byte.
- Primitive library: NOT, AND, OR, XOR, NAND, NOR, XNOR.
- Deterministic enumerative search over expression trees in increasing gate
  count, with deterministic depth tie-breaking.
- Exhaustive functional verification over all eight input assignments.
- Structural metrics: unique gate count, logic depth, maximum fanout, input
  fanout, output one-density, and a clearly labelled switching proxy.
- Verilog emission for inspection and downstream tool experiments.

The codebase also includes a multi-output DAG representation that structurally
shares identical subexpressions across outputs and verifies all output truth
tables. It is currently a representation/compiler layer; a dedicated search
procedure over multi-output networks remains future work.

## Research hypotheses to test (not established results)

1. A DAG-based representation with explicit reusable subgraphs can reduce
   multi-output gate count versus independently optimized expression trees.
2. Multi-objective search using gate count, depth, fanout, and switching
   activity can expose Pareto-optimal designs not found by a single scalar
   objective.
3. Motif libraries learned from solved subfunctions may improve search
   efficiency while preserving exact functional correctness.
4. Counterexample-guided or SAT-assisted search may scale beyond tiny truth
   tables more effectively than exhaustive enumeration.

## Experimental sequence

1. Reproduce the baseline results from a clean environment.
2. Exhaustively validate all generated circuits against their target truth
   tables; preserve the input ordering convention in every artifact.
3. Compare candidate circuits against at least one independent synthesis flow
   using the same gate library and cost assumptions.
4. Add DAG sharing and multi-output benchmarks, retaining the expression-tree
   baseline as a control.
5. Add a Pareto-front search and evaluate trade-offs rather than declaring one
   metric universally best.
6. Export Verilog and evaluate mapped area/delay only after choosing and
   documenting a real cell library and toolchain.

## Claims policy

Do not describe a candidate as physically faster, lower-power, smaller silicon,
novel, or patentable based only on truth-table gate count or logic depth. Those
claims require mapped netlists, target-library characterization, timing and
power analysis, reproducible baselines, and prior-art review.
