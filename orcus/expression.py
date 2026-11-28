"""Immutable expression trees used by the enumerative baseline."""

from __future__ import annotations

from dataclasses import dataclass

from .gates import GATE_LIBRARY, apply_gate


@dataclass(frozen=True, slots=True)
class Expr:
    op: str
    args: tuple["Expr", ...] = ()
    value: int | None = None
    truth: int = 0

    @property
    def gate_count(self) -> int:
        return (1 if self.op in GATE_LIBRARY else 0) + sum(a.gate_count for a in self.args)

    @property
    def depth(self) -> int:
        return 0 if self.op in {"VAR", "CONST"} else 1 + max(a.depth for a in self.args)

    @property
    def structural_key(self) -> tuple:
        keys = tuple(a.structural_key for a in self.args)
        if self.op in GATE_LIBRARY and GATE_LIBRARY[self.op].commutative:
            keys = tuple(sorted(keys))
        return (self.op, self.value, keys)

    def render(self, names: tuple[str, ...] | None = None) -> str:
        if self.op == "VAR":
            if names is None:
                return f"x{self.value}"
            return names[self.value or 0]
        if self.op == "CONST":
            return str(self.value)
        if self.op == "NOT":
            return f"NOT({self.args[0].render(names)})"
        symbol = {"AND": "&", "OR": "|", "XOR": "^", "NAND": "NAND", "NOR": "NOR", "XNOR": "XNOR"}[self.op]
        return f"({self.args[0].render(names)} {symbol} {self.args[1].render(names)})"


def variable(index: int, truth: int) -> Expr:
    return Expr("VAR", value=index, truth=truth)


def constant(value: bool, truth: int, input_count: int) -> Expr:
    return Expr("CONST", value=int(value), truth=truth)


def gate(op: str, args: tuple[Expr, ...], mask: int) -> Expr:
    if op not in GATE_LIBRARY:
        raise ValueError(f"unsupported gate: {op}")
    truth = apply_gate(op, tuple(arg.truth for arg in args), mask)
    return Expr(op, args=args, truth=truth)
