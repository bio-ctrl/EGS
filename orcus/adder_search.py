"""Deterministic multi-objective search over generated adder architectures."""
from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .adder_architectures import (
    AdderArchitecture,
    build_kogge_stone_adder,
    build_ripple_carry_adder,
    build_sklansky_adder,
)


def generate_adder_candidates(width: int) -> tuple[AdderArchitecture, ...]:
    """Generate a fixed, reproducible architecture family for one width."""
    return (
        build_ripple_carry_adder(width),
        build_sklansky_adder(width),
        build_kogge_stone_adder(width),
    )


def dominates(left: tuple[int, int, int], right: tuple[int, int, int]) -> bool:
    """Return true when left is no worse in all minimized metrics and better in one."""
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def pareto_frontier(candidates: Iterable[AdderArchitecture]) -> tuple[AdderArchitecture, ...]:
    """Keep candidates not dominated on gate count, logic depth, and max fanout."""
    items = tuple(candidates)
    scores = {
        item.name: (
            item.metrics().gate_count,
            item.metrics().logic_depth,
            item.metrics().max_fanout,
        )
        for item in items
    }
    frontier = [
        item for item in items
        if not any(
            other.name != item.name and dominates(scores[other.name], scores[item.name])
            for other in items
        )
    ]
    return tuple(sorted(frontier, key=lambda item: item.name))


def search_report(width: int) -> dict:
    """Generate, exhaustively check (up to 8 bits), score, and rank candidates."""
    candidates = generate_adder_candidates(width)
    exhaustive = width <= 8
    vectors_per_operand = 1 << width if exhaustive else min(1 << width, 256)
    for candidate in candidates:
        for a in range(vectors_per_operand):
            for b in range(vectors_per_operand):
                if candidate.evaluate(a, b) != a + b:
                    raise AssertionError(
                        f"{candidate.name} failed at width={width}, a={a}, b={b}"
                    )
    frontier = {item.name for item in pareto_frontier(candidates)}
    results = []
    for candidate in candidates:
        metrics = asdict(candidate.metrics())
        results.append({
            "name": candidate.name,
            "metrics": metrics,
            "pareto_optimal": candidate.name in frontier,
            "verification": {
                "passed": True,
                "exhaustive": exhaustive,
                "vectors_checked": vectors_per_operand ** 2,
            },
            "verilog": candidate.emit_verilog(),
        })
    return {
        "width": width,
        "objective": ["minimize gate_count", "minimize logic_depth", "minimize max_fanout"],
        "search": {
            "generator": "fixed three-family architecture enumeration",
            "candidate_count": len(candidates),
            "pareto_candidate_count": len(frontier),
            "global_optimality_claim": False,
        },
        "candidates": results,
    }
