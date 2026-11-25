# Bit-level adder architecture experiment

ORCUS now contains two generators for the same unsigned addition function:

- **Ripple-carry:** each bit waits for the carry from the previous bit.
- **Kogge–Stone prefix:** carry information is combined in parallel stages.

The generators produce explicit Boolean DAGs, not opaque arithmetic operators.
Each candidate can be evaluated, measured, and exported as Verilog. Tests
exhaustively check every input pair for widths 1 through 4. The benchmark
extends to 32-bit structures and optionally invokes Yosys for an independent
generic-cell synthesis comparison.

## Reproduce

```bash
python -m unittest discover -s tests -v
python benchmarks/adder_architecture_suite.py --widths 4 8 16 32 --require-yosys --output artifacts/adder-architectures.json
```

## What this experiment can establish

It can establish that ORCUS can generate structurally different implementations
of one arithmetic function, verify small instances, and compare transparent
structural metrics and Yosys generic-cell results.

It cannot establish physical speed, power, energy, silicon area, or superiority
to commercial EDA. Kogge–Stone structures can reduce logical carry depth while
using more wiring and gates; physical implementation can change the trade-off.
A useful result must report all metrics, not select only the favorable one.

## Next research gate

Use these generators as the first reusable architecture family. Add a third
candidate (for example, carry-select or Brent–Kung), verify equivalence, compare
against a documented standard-cell library, and measure routed PPA before
making hardware-performance claims.
