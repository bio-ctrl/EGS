"""Compact truth-table representation for small combinational functions.

Rows are ordered lexicographically by input tuple, with input 0 as the most
significant assignment bit. Truth-table output row ``r`` is stored in bit ``r``.
For three inputs, the representation is therefore an integer in [0, 255].
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True, slots=True)
class TruthTable:
    input_count: int
    bits: int

    def __post_init__(self) -> None:
        if not 1 <= self.input_count <= 8:
            raise ValueError("input_count must be between 1 and 8")
        if not isinstance(self.bits, int):
            raise TypeError("bits must be an integer")
        if self.bits < 0 or self.bits > self.mask:
            raise ValueError(f"bits must fit in {self.row_count} rows")

    @property
    def row_count(self) -> int:
        return 1 << self.input_count

    @property
    def mask(self) -> int:
        return (1 << self.row_count) - 1

    @classmethod
    def constant(cls, input_count: int, value: bool) -> "TruthTable":
        rows = 1 << input_count
        return cls(input_count, (1 << rows) - 1 if value else 0)

    @classmethod
    def variable(cls, input_count: int, variable_index: int) -> "TruthTable":
        if not 0 <= variable_index < input_count:
            raise IndexError("variable_index is outside the input range")
        bits = 0
        for row, assignment in enumerate(product((0, 1), repeat=input_count)):
            if assignment[variable_index]:
                bits |= 1 << row
        return cls(input_count, bits)

    @classmethod
    def from_callable(
        cls, input_count: int, function: Callable[..., bool | int]
    ) -> "TruthTable":
        bits = 0
        for row, assignment in enumerate(product((0, 1), repeat=input_count)):
            if bool(function(*assignment)):
                bits |= 1 << row
        return cls(input_count, bits)

    @classmethod
    def from_binary(cls, input_count: int, value: str) -> "TruthTable":
        cleaned = value.replace("_", "").replace(" ", "")
        if len(cleaned) != 1 << input_count or set(cleaned) - {"0", "1"}:
            raise ValueError("binary input must contain one 0/1 digit per row")
        bits = sum((digit == "1") << i for i, digit in enumerate(cleaned))
        return cls(input_count, bits)

    @classmethod
    def from_int(cls, input_count: int, value: int) -> "TruthTable":
        return cls(input_count, value)

    def output(self, assignment: Sequence[int | bool]) -> int:
        row = assignment_to_row(assignment, self.input_count)
        return (self.bits >> row) & 1

    def outputs(self) -> tuple[int, ...]:
        return tuple((self.bits >> row) & 1 for row in range(self.row_count))

    def binary(self) -> str:
        return "".join(str(value) for value in self.outputs())

    def hex(self) -> str:
        width = max(1, (self.row_count + 3) // 4)
        return f"0x{self.bits:0{width}x}"

    def _check_compatible(self, other: "TruthTable") -> None:
        if self.input_count != other.input_count:
            raise ValueError("truth tables have different input counts")

    def __invert__(self) -> "TruthTable":
        return TruthTable(self.input_count, (~self.bits) & self.mask)

    def __and__(self, other: "TruthTable") -> "TruthTable":
        self._check_compatible(other)
        return TruthTable(self.input_count, self.bits & other.bits)

    def __or__(self, other: "TruthTable") -> "TruthTable":
        self._check_compatible(other)
        return TruthTable(self.input_count, self.bits | other.bits)

    def __xor__(self, other: "TruthTable") -> "TruthTable":
        self._check_compatible(other)
        return TruthTable(self.input_count, self.bits ^ other.bits)

    def __len__(self) -> int:
        return self.row_count

    def __str__(self) -> str:
        return f"TruthTable(n={self.input_count}, bits={self.hex()}, rows={self.binary()})"


def variables(input_count: int) -> tuple[TruthTable, ...]:
    """Return truth tables for x0 .. x(n-1)."""
    return tuple(TruthTable.variable(input_count, i) for i in range(input_count))


def assignment_to_row(assignment: Sequence[int | bool], input_count: int) -> int:
    """Validate a Boolean assignment and convert it to its truth-table row."""
    if len(assignment) != input_count:
        raise ValueError("assignment has the wrong number of inputs")
    row = 0
    for item in assignment:
        if not isinstance(item, (bool, int)) or item not in (0, 1):
            raise ValueError("assignments must contain only Boolean 0/1 values")
        row = (row << 1) | int(item)
    return row
