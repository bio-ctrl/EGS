# General Associative Architecture Search v1

## Purpose

The previous ORCUS adder experiment selected among three hand-coded families. This experiment adds a more general topology generator: given a bit-vector operator and a set of operands, ORCUS enumerates distinct labeled binary-tree dataflow graphs for associative, commutative operators (add, and, or, and xor).

The generator recursively enumerates binary tree shapes and operand permutations, canonicalizes commutative child order, emits typed BitVectorGraph instances, and enforces a hard candidate-count limit.

## Verification

Each generated graph is evaluated against the operator's direct reference function. Exhaustive checking is performed when the total input width is at most 16 bits. The initial CI workload uses four 2-bit operands, so all 2^8 = 256 input assignments are checked for every candidate.

## Ranking

Candidates are compared using operation count, logic depth, and maximum fanout. The Pareto frontier is only relative to the generated candidate set and these structural metrics. It is not a proof of global optimality.

The benchmark exports every candidate to Verilog and runs Yosys synthesis when available. The CI run requires Yosys and records generic-cell counts.

## Initial experiment boundary

This is a genuine move from selecting among three named adder implementations to generating a family of dataflow topologies from an operator grammar. It is not unrestricted circuit invention. The grammar only covers associative, commutative binary trees; it does not yet search arbitrary Boolean networks, state elements, pipeline schedules, memory structures, or physical layouts.

Yosys generic-cell counts are not standard-cell area, timing, power, energy, routing, or silicon measurements. No claim of architectural novelty or commercial advantage is made. A stronger result requires broader benchmark coverage, formal equivalence, technology mapping, and physical implementation.
