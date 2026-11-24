# ORCUS v0.1 technical specification

## 1. Function encoding

For an `n`-input function, enumerate assignments in lexicographic order over
`(0, 1)^n`. Input `x0` is the most-significant assignment bit. Row `r` is stored
in bit `r` of an integer. Therefore, an `n`-input truth table occupies exactly
`2^n` bits. For `n=3`, the state space contains 256 distinct Boolean functions.

## 2. Primitive library

| Gate | Arity | Bit-parallel implementation |
|---|---:|---|
| NOT | 1 | `~a & mask` |
| AND | 2 | `a & b` |
| OR | 2 | `a | b` |
| XOR | 2 | `a ^ b` |
| NAND | 2 | `~(a & b) & mask` |
| NOR | 2 | `~(a | b) & mask` |
| XNOR | 2 | `~(a ^ b) & mask` |

The current binary gate set is commutative. The enumerator canonicalizes
operand order to avoid symmetric duplicates.

## 3. Enumerative search recurrence

The current objective is minimum expression-tree gate count, with logic depth
as the deterministic tie-breaker. Input variables and constants are cost zero.

For each cost `c` from 1 through the configured bound:

- Unary gate candidates use a child with cost `c - 1`.
- Binary gate candidates combine children with costs `i` and `j`, where
  `i + j + 1 = c`.
- For each newly reached truth table, keep its best candidate at that cost by
  `(logic_depth, structural_key)`.
- Do not replace a truth function already found at lower gate cost.

This is exact for the stated expression-tree objective because every
combinational expression has a root gate and child expression trees whose gate
counts sum to `c - 1`. It is not an exact optimizer for arbitrary multi-output
DAG networks, mapped standard cells, or physical implementations.

## 4. Circuit IR

`Circuit` represents one output. `CircuitNetwork` represents multiple named
outputs and performs structural common-subexpression sharing across those
outputs. Both representations use a topologically ordered node list and
support exhaustive evaluation over all input assignments.

## 5. Validation

The test suite verifies:

- Truth-table encoding, bitwise operators, and invalid-input handling.
- Circuit evaluation and metric calculations.
- Search completeness for the 256 three-input Boolean functions under the
  configured library and four-gate bound.
- Every catalogued function by recompiling its expression and comparing the
  resulting circuit truth table with the target over all eight rows.
- Multi-output common-subexpression sharing and output-level correctness.
- Verilog structure generation and identifier validation.

## 6. Interpretation boundary

The enumerator counts primitive gates in expression trees. The compiled IR
counts unique gates after structural deduplication. Neither is a mapped area
measurement. Logic depth is a unit-gate-level count, not delay in seconds. The
output toggle proxy assumes uniform, independent input vectors and is not
power estimation. Real hardware claims require a defined cell library, timing
constraints, mapping, and physical analysis.
