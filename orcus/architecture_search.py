"""Bounded, deterministic associative architecture search.

Canonicalization is intentionally limited to commutative binary-tree forms in
this module's declared associative/commutative grammar. It is not general DAG
isomorphism. Runtime is reported as environment-dependent metadata.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import permutations
import json
from time import perf_counter
from typing import Iterable, Iterator

from .bitvector import BitVectorGraph, DataNode, DataOutput, DataPort

_ASSOCIATIVE_COMMUTATIVE = {"add", "and", "or", "xor"}
CANONICALIZER_VERSION = "ac-tree-v1"


@dataclass(frozen=True, slots=True)
class ArchitectureCandidate:
    name: str
    graph: BitVectorGraph
    topology: tuple
    digest: str


def _tree_shapes(items: tuple[str, ...]) -> Iterator[tuple | str]:
    if len(items) == 1:
        yield items[0]
        return
    for split in range(1, len(items)):
        for left in _tree_shapes(items[:split]):
            for right in _tree_shapes(items[split:]):
                yield (left, right)


def _tree_key(tree: tuple | str) -> str:
    return json.dumps(tree, separators=(",", ":"), ensure_ascii=True)


def _canonical(tree: tuple | str) -> tuple | str:
    if isinstance(tree, str):
        return tree
    left, right = (_canonical(child) for child in tree)
    return (left, right) if _tree_key(left) <= _tree_key(right) else (right, left)


def _build_graph(op: str, width: int, input_names: tuple[str, ...],
                 tree: tuple | str) -> BitVectorGraph:
    nodes: list[DataNode] = []
    serial = 0

    def emit(item: tuple | str) -> str:
        nonlocal serial
        if isinstance(item, str):
            return item
        left, right = emit(item[0]), emit(item[1])
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


def _candidate_digest(op: str, width: int, input_names: tuple[str, ...],
                      topology: tuple | str) -> str:
    payload = {
        "canonicalizer": CANONICALIZER_VERSION,
        "operator": op,
        "width": width,
        "inputs": [{"name": name, "width": width} for name in input_names],
        "outputs": [{"name": "result", "width": width}],
        "topology": topology,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def _validate(op: str, operand_count: int, width: int, max_candidates: int) -> None:
    if op not in _ASSOCIATIVE_COMMUTATIVE:
        raise ValueError(f"unsupported associative/commutative operator: {op}")
    if not 2 <= operand_count <= 8:
        raise ValueError("operand_count must be between 2 and 8")
    if not 1 <= width <= 64:
        raise ValueError("width must be between 1 and 64")
    if not isinstance(max_candidates, int) or isinstance(max_candidates, bool) or max_candidates < 1:
        raise ValueError("max_candidates must be a positive integer")


def _enumerate(op: str, operand_count: int, width: int, max_candidates: int):
    _validate(op, operand_count, width, max_candidates)
    names = tuple(f"x{i}" for i in range(operand_count))
    seen: set[str] = set()
    candidates: list[ArchitectureCandidate] = []
    budget_exhausted = False
    generation_attempts = 0

    # Permutations/tree shapes are streamed; no combinatorial list is built.
    for order in permutations(names):
        for shape in _tree_shapes(order):
            generation_attempts += 1
            topology = _canonical(shape)
            digest = _candidate_digest(op, width, names, topology)
            if digest in seen:
                continue
            if len(candidates) >= max_candidates:
                budget_exhausted = True
                return candidates, budget_exhausted, generation_attempts
            seen.add(digest)
            graph = _build_graph(op, width, names, topology)
            candidates.append(ArchitectureCandidate(
                name=f"{op}_{operand_count}in_{digest[:12]}",
                graph=graph,
                topology=topology,
                digest=digest,
            ))
    return candidates, budget_exhausted, generation_attempts


def generate_associative_candidates(
    op: str, operand_count: int, width: int, max_candidates: int = 2000,
) -> tuple[ArchitectureCandidate, ...]:
    """Return up to max_candidates; budget exhaustion is a partial result, not an exception."""
    candidates, _, _ = _enumerate(op, operand_count, width, max_candidates)
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
    scores = {item.digest: _score(item) for item in items}
    return tuple(
        item for item in items
        if not any(
            other.digest != item.digest and _dominates(scores[other.digest], scores[item.digest])
            for other in items
        )
    )


def _baseline_score(op: str, operand_count: int, width: int) -> tuple[int, int, int]:
    names = tuple(f"x{i}" for i in range(operand_count))
    tree: tuple | str = names[0]
    for name in names[1:]:
        tree = (tree, name)
    graph = _build_graph(op, width, names, tree)
    metrics = graph.metrics()
    return (metrics.operation_count, metrics.logic_depth, metrics.max_fanout)


def run_search(op: str, operand_count: int, width: int,
               max_candidates: int = 2000) -> dict:
    """Run deterministic bounded search and return a complete partial/full report."""
    started = perf_counter()
    candidates, exhausted, attempts = _enumerate(
        op, operand_count, width, max_candidates
    )
    input_bits = operand_count * width
    exhaustive = input_bits <= 16
    baseline = _baseline_score(op, operand_count, width)
    frontier = {item.digest for item in pareto_candidates(candidates)}
    reports = []
    wins = ties = regressions = tradeoffs = 0

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
            verification["status"] = "exhaustive-pass" if verification["passed"] else "failed"
            if not verification["passed"]:
                raise AssertionError(f"candidate failed equivalence: {candidate.name}")
        else:
            verification = {
                "passed": None, "exhaustive": False, "vectors_checked": 0,
                "input_bits": input_bits, "status": "not-run",
            }

        score = _score(candidate)
        candidate_wins = _dominates(score, baseline)
        baseline_wins = _dominates(baseline, score)
        if candidate_wins:
            outcome = "win"
            wins += 1
        elif score == baseline:
            outcome = "tie"
            ties += 1
        elif baseline_wins:
            outcome = "regression"
            regressions += 1
        else:
            outcome = "tradeoff"
            tradeoffs += 1

        reports.append({
            "name": candidate.name,
            "digest": candidate.digest,
            "canonicalizer_version": CANONICALIZER_VERSION,
            "topology": candidate.topology,
            "metrics": asdict(candidate.graph.metrics()),
            "baseline_metrics": {
                "operation_count": baseline[0],
                "logic_depth": baseline[1],
                "max_fanout": baseline[2],
            },
            "outcome_vs_left_associated_baseline": outcome,
            "pareto_optimal_in_explored_set": candidate.digest in frontier,
            "verification": verification,
            "verilog": candidate.graph.emit_verilog(candidate.name),
        })

    elapsed = perf_counter() - started
    return {
        "schema_version": "orcus-architecture-search-report-v2",
        "operator": op,
        "operand_count": operand_count,
        "width": width,
        "input_bits": input_bits,
        "config": {"max_candidates": max_candidates},
        "canonicalizer_version": CANONICALIZER_VERSION,
        "search_space": {
            "grammar": "labeled full binary trees over declared associative/commutative bit-vector operators",
            "candidate_count": len(candidates),
            "generation_attempts": attempts,
            "unique_candidate_count": len(candidates),
            "candidate_budget_exhausted": exhausted,
            "stop_reason": "candidate-budget-exhausted" if exhausted else "completed",
            "exhaustive_equivalence": exhaustive,
            "pareto_candidate_count": len(frontier),
            "global_optimality_claim": False,
        },
        "outcomes": {
            "wins": wins, "ties": ties, "regressions": regressions,
            "tradeoffs": tradeoffs,
        },
        "runtime": {
            "elapsed_seconds": elapsed,
            "deterministic": False,
            "note": "Runtime is environment-dependent; candidate order and identities are deterministic.",
        },
        "candidates": reports,
    }
