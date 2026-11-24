"""Gate-library definitions and bit-parallel Boolean evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class GateSpec:
    name: str
    arity: int
    function: Callable[..., int]
    commutative: bool = False

    def apply(self, operands: tuple[int, ...], mask: int) -> int:
        if len(operands) != self.arity:
            raise ValueError(f"{self.name} expects {self.arity} operands")
        return self.function(*operands) & mask


def _not(a: int) -> int: return ~a
def _and(a: int, b: int) -> int: return a & b
def _or(a: int, b: int) -> int: return a | b
def _xor(a: int, b: int) -> int: return a ^ b
def _nand(a: int, b: int) -> int: return ~(a & b)
def _nor(a: int, b: int) -> int: return ~(a | b)
def _xnor(a: int, b: int) -> int: return ~(a ^ b)

GATE_LIBRARY: dict[str, GateSpec] = {
    "NOT": GateSpec("NOT", 1, _not),
    "AND": GateSpec("AND", 2, _and, True),
    "OR": GateSpec("OR", 2, _or, True),
    "XOR": GateSpec("XOR", 2, _xor, True),
    "NAND": GateSpec("NAND", 2, _nand, True),
    "NOR": GateSpec("NOR", 2, _nor, True),
    "XNOR": GateSpec("XNOR", 2, _xnor, True),
}

DEFAULT_GATES = tuple(GATE_LIBRARY)


def apply_gate(name: str, operands: tuple[int, ...], mask: int) -> int:
    try:
        spec = GATE_LIBRARY[name]
    except KeyError as exc:
        raise ValueError(f"unsupported gate: {name}") from exc
    return spec.apply(operands, mask)
