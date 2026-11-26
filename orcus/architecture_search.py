"""Bounded architecture enumeration for associative bit-vector dataflow.

Unlike the adder-family experiment, this generator builds graph topologies from
an operator and an input set. It enumerates labeled binary trees for associative,
commutative operations, canonicalizes equivalent commutative tree encodings,
then verifies and ranks the resulting architectures. It is still a bounded
search over a defined grammar, not unrestricted circuit invention.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import permutations
from typing import Iterable

from .bitvector import BitVectorGraph, DataNode, DataOutput, DataPort

_ASSOCIATIVE_COMMUTATIVE = {"add", "and", "or", "xor"}


@dataclass(frozen=True, slots=True)
class ArchitectureCandidate:
    name: str
    graph: BitVectorGraph
    topology: tuple


def _tree_shapes(items: tuple[str, ...]) -> Iterable[tuple]:
    """Yield every ordered full binary tree over items in their given order."""
    if len(items) == 1:
        yield items[0]
        return
    for split in range(1, len(items)):
        for left in _tree_shapes(items[:split]):
            for right in _tree_shapes(items[split:]):
                yield (left, right)


def _canonical(tree: tuple | str) -> tuple | str:
    if isinstance(tree, str):
        return tree
    left, right = (_canonical(child) for child in tree)
    return (left, right) if repr(left) <= repr(right) else (right, left)


def _build_graph(op: str, width: int, input_names: tuple[str, ...],
                 tree: tuple | str) -> BitVectorGraph:
    nodes: list[DataNode] = []
    serial = 0

    def emit(item: tuple | str) -> str:
        nonlocal serial
        if isinstance(item, str):
            return item
        left = emit(item[0])
        right = emit(item[1])
        node_id = f"n{serial}"
        serial += 1
        nodes.append(DataNode(node_id, op, (left, right), width))
        return node_id

    root = emit(tree)
    return BitVectorGraph(
        inputs=tuple(DataPort(name, width) for name in input_names),
        nodes=tuple(nodes),
        outputs=(DataOutput("result", root, width),),
    )


def generate_associative_candidates(
    op: str, operand_count: int, width: int, max_candidates: int = 2000,
) -> tuple[ArchitectureCandidate, ...]:
    """Enumerate distinct labeled binary-tree topologies within a hard cap."""
    if op not in _ASSOCIATIVE_COMMUTATIVE:
        raise ValueError(f"unsupported associative/commutative operator: {op}")
    if not 2 <= operand_count <= 8:
        raise ValueError("operand_count must be between 2 and 8")
    if not 1 <= width <= 64:
        raise ValueError("width must be between 1 and 64")
    if max_candidates < 1:
        raise ValueError("max_candidates must be positive")

    names = tuple(f"x{i}" for i in range(operand_count))
    unique: dict[tuple, tuple] = {}
    for order in permutations(names):
        for shape in _tree_shapes(order):
            key = _canonical(shape)
            unique.setdefault(key, key)
            if len(unique) > max_candidates:
                raise ValueError(
                    f"search exceeded max_candidates={max_candidates}; "
                    "reduce operand_count or raise the explicit cap"
                )

    candidates = []
    for index, topology in enumerate(sorted(unique, key=repr)):
        graph = _build_graph(op, width, names, topology)
        candidates.append(ArchitectureCandidate(
            name=f"{op}_{operand_count}in_{index:04d}",
            graph=graph,
            topology=topology,
        ))
    return tuple(candidates)


def _apply(op: str, values: list[int], width: int) -> int:
    mask = (1 << width) - 1
    if op == "add":
        result = sum(values)
    elif op == "and":
        result = values[0]
        for value in values[1:]:
            result &= value
    elif op == "or":
        result = 0
        for value in values:
            result |= value
    elif op == "xor":
        result = 0
        for value in values:
            result ^= value
    else:
        raise ValueError(op)
    return result & mask


def _score(candidate: ArchitectureCandidate) -> tuple[int, int, int]:
    metrics = candidate.graph.metrics()
    return (metrics.operation_count, metrics.logic_depth, metrics.max_fanout)


def _dominates(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def pareto_candidates(
    candidates: Iterable[ArchitectureCandidate],
) -> tuple[ArchitectureCandidate, ...]:
    items = tuple(candidates)
    return tuple(
        item for item in items
        if not any(
            other.name != item.name and _dominates(_score(other), _score(item))
            for other in items
        )
    )


def run_search(op: str, operand_count: int, width: int,
               max_candidates: int = 2000) -> dict:
    """Generate, exhaustively verify when feasible, and rank graph topologies."""
    candidates = generate_associative_candidates(
        op, operand_count, width, max_candidates=max_candidates
    )
    input_bits = operand_count * width
    exhaustive = input_bits <= 16
    frontier = {item.name for item in pareto_candidates(candidates)}
    reports = []
    for candidate in candidates:
        if exhaustive:
            verification = asdict(candidate.graph.verify_exhaustive(
                lambda assignment: {
                    "result": _apply(
                        op, [assignment[name] for name in sorted(assignment)], width
                    )
                },
                max_input_bits=16,
            ))
            if not verification["passed"]:
                raise AssertionError(f"candidate failed equivalence: {candidate.name}")
        else:
            verification = {
                "passed": False,
                "exhaustive": False,
                "vectors_checked": 0,
                "input_bits": input_bits,
                "status": "requires_external_formal_proof",
            }
        metrics = asdict(candidate.graph.metrics())
        reports.append({
            "name": candidate.name,
            "topology": repr(candidate.topology),
            "metrics": metrics,
            "pareto_optimal": candidate.name in frontier,
            "verification": verification,
            "verilog": candidate.graph.emit_verilog(candidate.name),
        })
    return {
        "operator": op,
        "operand_count": operand_count,
        "width": width,
        "input_bits": input_bits,
        "search_space": {
            "grammar": "labeled full binary trees over associative/commutative bit-vector operator",
            "candidate_count": len(candidates),
            "exhaustive_equivalence": exhaustive,
            "pareto_candidate_count": len(frontier),
            "global_optimality_claim": False,
        },
        "candidates": reports,
    }
