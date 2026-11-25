# Joint multi-output search: first five-case results

## Reproduction

Run:

```bash
python benchmarks/joint_search_suite.py --max-gates 3 --require-yosys --output artifacts/joint-suite.json
```

The recorded CI run used Python 3.11.18 and Yosys 0.52. Each case used
three Boolean inputs, the seven-gate ORCUS primitive library, a maximum
three-gate expression search depth, a 100,000 generated-expression limit,
and a 50,000 output-combination limit.

## Results

All five baseline networks and all five joint-search networks passed exhaustive
truth-table verification.

| Case | Structural DAG result | Yosys generic-cell result |
|---|---:|---:|
| shared_product | 1 fewer gate | Tie |
| half_adder | Tie | Tie |
| dual_mux | Tie | Tie |
| parity_and_or | Tie | Tie |
| two_bit_decoder | 1 fewer gate | Tie |

Summary:

- Structural gate count improved in 2 of 5 cases.
- Structural gate count tied in 3 of 5 cases.
- Structural regressions: 0 of 5 cases.
- Yosys generic-cell count improved in 0 of 5 cases; all five cases tied after
  Yosys synthesis.
- All five joint searches reported bounded/truncated exploration; these are
  best candidates found inside the configured search limits, not global
  optima.

## Interpretation

This is useful evidence that the joint candidate search can find alternative
shared DAG representations that reduce the prototype's own structural gate
count on some small cases. It is **not** evidence that ORCUS beats Yosys:
Yosys's independent synthesis flow reduced the baseline and joint candidates
to the same generic-cell count in every case.

The joint search also takes longer than the selected-expression baseline on
these small examples (roughly 0.6 seconds versus roughly 0.02 seconds per case
on the recorded CI runner). The current method is therefore not yet a faster
replacement for established synthesis.

Yosys generic internal cells are not a foundry standard-cell library. No mapped
area, timing, power, energy, routing, FPGA, or silicon result was measured.
This five-case, three-input suite is a research smoke benchmark, not a
representative industry benchmark suite. The next technical gate is to improve
the search objective/coverage and test on larger, public benchmark circuits
with an explicitly matched technology library and stronger independent
baselines.
