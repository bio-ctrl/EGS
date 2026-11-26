# ORCUS architecture search v1

This experiment turns the adder generators into a deterministic candidate
search loop.

## Search procedure

1. Generate ripple-carry, Sklansky, and Kogge–Stone implementations for the
   same unsigned addition function.
2. Evaluate every candidate on the same input domain. Widths up to eight are
   checked exhaustively; larger widths use a deterministic bounded sample.
3. Measure gate count, logic depth, and maximum fanout from the explicit DAG.
4. Compute the Pareto frontier. A candidate is removed only if another is no
   worse on all three minimized metrics and strictly better on at least one.
5. Export all candidates as Verilog for independent synthesis.

## Reproduce

```bash
python -m unittest discover -s tests -v
python benchmarks/architecture_search_suite.py --widths 4 8 16 32 --output artifacts/architecture-search.json
```

## Interpretation

This is an enumerative design-space search over three known adder families,
not autonomous invention and not a proof of global optimality. The Pareto
frontier exposes trade-offs rather than hiding them behind one arbitrary score.
The benchmark also invokes Yosys when installed and records generic cell counts.
Generic-cell count is not physical area, delay, power, or routing. A real
hardware advantage requires controlled mapping and physical implementation
against a documented cell library.
