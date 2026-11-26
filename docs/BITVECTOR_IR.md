# Typed bit-vector dataflow IR

ORCUS now has a reusable, width-aware representation for combinational
computations. Unlike the initial truth-table engine, this IR represents
multi-bit values and typed operations rather than enumerating only tiny
Boolean functions.

## Supported operations

- Unsigned add and subtract (results wrap to the declared output width)
- Bitwise AND, OR, XOR, and NOT
- 1-bit-select multiplexers
- Equality comparison
- Logical left and right shifts
- Width-checked constants

Every graph validates signal names, widths, operator arity, dependencies, and
output types when constructed. Nodes must be topologically ordered. Evaluation
is deterministic, and exhaustive verification enumerates every input vector
only when the total input width is within the configured limit. Otherwise the
report explicitly says that exhaustive verification was not performed.

## Reproduce

```bash
python -m unittest discover -s tests -v
```

## What this unlocks

This is the common representation needed to compare different implementations
of arithmetic, muxing, comparisons, and data-path functions in one framework.
It is not yet an architecture-discovery algorithm: candidate generation,
rewriting, search policies, and independent synthesis comparisons are separate
research tasks. Structural operation count and depth are not physical PPA.
