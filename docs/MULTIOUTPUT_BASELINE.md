# Multi-output synthesis baseline

## Purpose

`orcus.multioutput.synthesize_multi_output` combines named Boolean output
functions into one explicit DAG. It reuses the current deterministic
single-output enumerator, then structurally shares identical expression
subgraphs across outputs.

## Reported quantities

- `independent_gate_count`: sum of selected single-output expression gate
  counts, treating each output as a separate implementation.
- `shared_gate_count`: unique gate nodes in the combined DAG.
- `gates_saved`: independent count minus shared count.
- `logic_depth` and fanout: metrics of the combined DAG.
- Exhaustive truth-table verification: every output is checked on every input
  assignment by `CircuitNetwork.verify`.

## Interpretation limits

This is a controlled structural-sharing baseline, not a joint global
multi-output optimizer. Each output first receives the deterministic
single-output minimum-gate expression selected by the existing enumerator.
The combined network can share identical subexpressions in those selected
expressions, but it does not explore alternative expressions jointly.

A positive `gates_saved` value demonstrates structural sharing for that
benchmark only. It does not establish better mapped area, timing, power, or
silicon performance. Those require a fixed technology library and independent
synthesis/physical-design measurements.

## Next experiment

Extend the enumerator to retain multiple non-dominated expressions per truth
table, then search combinations jointly across outputs. Compare the resulting
Pareto frontier against independent single-output synthesis and established
tools under identical gate and cost assumptions.
