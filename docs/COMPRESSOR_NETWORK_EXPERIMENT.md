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

## Recorded CI result

Run: [ORCUS CI 145](https://github.com/bio-ctrl/EGS/actions/runs/45725047695), Yosys 0.52,
four unsigned 3-bit operands, 4,096 possible input combinations.

All nine candidates passed exhaustive functional checking and Yosys SAT equivalence.
The direct arithmetic reference synthesized to 43 generic cells.

| Reduction schedule | Final adder | Candidate cells | Delta vs reference |
|---|---:|---:|---:|
| Wallace | Ripple | 40 | -3 |
| Wallace | Kogge–Stone | 43 | 0 |
| Wallace | Sklansky | 44 | +1 |
| Reversed Wallace | Ripple | 41 | -2 |
| Reversed Wallace | Kogge–Stone | 45 | +2 |
| Reversed Wallace | Sklansky | 45 | +2 |
| Dadda | Ripple | 43 | 0 |
| Dadda | Kogge–Stone | 49 | +6 |
| Dadda | Sklansky | 45 | +2 |

Two of nine candidates used fewer generic cells than the direct arithmetic
reference, two tied, and five used more. The best result was Wallace + ripple
at 40 versus 43 generic cells (about 7% fewer). This is a narrow, small-width
synthesis result—not evidence that ORCUS beats Yosys/ABC generally, and not a
measurement of standard-cell area, routed delay, power, or physical PPA.
