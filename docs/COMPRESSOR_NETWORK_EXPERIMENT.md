# Multi-operand compressor-network experiment

## Purpose
This experiment extends ORCUS from associative binary-tree enumeration to
bit-heap reduction for unsigned multi-operand addition. It provides established
Wallace and Dadda reference schedules plus a reversed-order Wallace variant as
a bounded search perturbation.

## Reproduction
```bash
python -m unittest tests.test_compressor -v
python benchmarks/compressor_network_suite.py --operands 4 --width 3 --require-yosys --output /tmp/orcus-compressor.json
```

The nine schedule/final-adder combinations are compared against a direct arithmetic reference. The benchmark reports structural gate count, logic depth and fanout, performs
exhaustive checking when the total input space is within its configured limit,
and invokes Yosys for an equivalence miter and generic synthesis.

## Interpretation
Wallace and Dadda are established architectures, not ORCUS inventions.
Kogge–Stone and Sklansky final adders are established architectures. Reversing the deterministic grouping order is an experimental search variant,
not a novelty claim. Yosys generic-cell statistics are not mapped area, routed
delay, or power. A physical advantage requires a fixed standard-cell library,
constraints, placement and routing, timing analysis, and activity-based power
analysis. Report every candidate, including ties and regressions.
