"""Canonical benchmark targets for three-input combinational logic."""

from __future__ import annotations

from .truth_table import TruthTable


def majority3(a: int, b: int, c: int) -> int:
    return int((a + b + c) >= 2)


def parity3(a: int, b: int, c: int) -> int:
    return a ^ b ^ c


def mux3(a: int, b: int, c: int) -> int:
    """A is select; return B when A=1, otherwise C."""
    return b if a else c


def comparator_ge_2(a: int, b: int, c: int) -> int:
    return int((a + b + c) >= 2)


def benchmark_targets() -> dict[str, TruthTable]:
    return {
        "majority3": TruthTable.from_callable(3, majority3),
        "parity3": TruthTable.from_callable(3, parity3),
        "mux3": TruthTable.from_callable(3, mux3),
    }
