# Bounded joint multi-output search

## What changed

The new joint search retains several structurally different expression trees for each Boolean truth table, then evaluates combinations as one shared directed acyclic graph (DAG).

The selected network is ranked by unique shared gate count, network logic depth, maximum fanout, total expression-tree gate count, and a deterministic structural tie-break.

Every candidate network is checked against every row of every target truth table before it can be selected.

## Why this differs from the first baseline

The original multi-output baseline selected one single-output implementation per target and only then deduplicated identical subexpressions. This search keeps alternative implementations alive. A different implementation of one output may expose a reusable subcircuit that makes the combined network smaller.

## Search limits

This is a bounded research algorithm, not a global-optimality proof. The initial implementation supports 1–3 inputs and uses configurable limits for maximum expression-tree gate count, candidates retained per truth table per gate-cost layer, total generated expressions, and output-candidate combinations evaluated.

The result field search_truncated is true when a configured bound prunes part of the search space. A truncated result is only the best candidate found within the explored subset.

## What the metrics do not prove

Gate count, depth, and fanout are technology-independent structural metrics. They do not establish mapped cell area, physical delay, energy, power, routing quality, or silicon superiority. Those claims require a fixed cell library, an independent synthesis flow, and physical or FPGA measurements.

## Reproduction

Run: python -m unittest discover -s tests -v

The unit tests check candidate diversity, exhaustive output correctness, invalid inputs, and explicit reporting when the combination limit truncates the search.
