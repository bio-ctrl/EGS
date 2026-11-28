# Experiment protocol

Every experiment record must preserve:

- ORCUS version and source revision.
- Python version and host platform.
- Input count, target truth table, and assignment bit ordering.
- Exact enabled gate set and maximum search depth.
- Search runtime and number of distinct truth functions reached.
- Circuit gate count, depth, and fanout metrics.
- Exhaustive verification result.

## Fair-comparison requirements

- Use the same primitive gate set for each candidate and baseline.
- State whether constants and inverted outputs are free or counted.
- State whether gate count means expression-tree nodes or unique DAG nodes.
- Keep mapping, placement, routing, and physical estimation separate from
  technology-independent logic metrics.
- Report all benchmark cases, including failures and timeouts.
- Repeat timing measurements and report median and dispersion before making
  runtime claims.

## Switching proxy

`output_toggle_proxy` is computed as `2p(1-p)` for the output under
uniform, independent input vectors, where `p` is the fraction of truth-table
rows producing one. This is a simple activity proxy. It is not a power model,
does not include glitches, capacitance, clocking, cell characterization, or
realistic workload probabilities.
