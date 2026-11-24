"""Small, deterministic Verilog emitter for the supported gate-level IR."""

from __future__ import annotations

import re

from .circuit import Circuit


_VERILOG_OPS = {
    "NOT": lambda a: f"~{a[0]}",
    "AND": lambda a: f"({a[0]} & {a[1]})",
    "OR": lambda a: f"({a[0]} | {a[1]})",
    "XOR": lambda a: f"({a[0]} ^ {a[1]})",
    "NAND": lambda a: f"~({a[0]} & {a[1]})",
    "NOR": lambda a: f"~({a[0]} | {a[1]})",
    "XNOR": lambda a: f"~({a[0]} ^ {a[1]})",
}


def emit_verilog(circuit: Circuit, module_name: str = "orcus_candidate") -> str:
    """Emit a combinational Verilog module; this does not perform technology mapping."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", module_name):
        raise ValueError("module_name must be a valid Verilog identifier")

    inputs = [f"x{i}" for i in range(circuit.input_count)]
    source_names: dict[str, str] = {}
    for node in circuit.nodes:
        if node.op == "VAR":
            assert node.value is not None
            if not 0 <= node.value < circuit.input_count:
                raise ValueError(f"input node {node.node_id} references invalid input {node.value}")
            source_names[node.node_id] = inputs[node.value]
        else:
            source_names[node.node_id] = node.node_id

    lines = [
        f"module {module_name}({', '.join(inputs)}, y);",
        f"  input {', '.join(inputs)};",
        "  output y;",
    ]

    # Declare all internal nets before assignments to avoid implicit-net behavior.
    for node in circuit.nodes:
        if node.op != "VAR":
            lines.append(f"  wire {node.node_id};")

    for node in circuit.nodes:
        if node.op == "VAR":
            continue
        if node.op == "CONST":
            expression = f"1'b{int(bool(node.value))}"
        else:
            try:
                expression = _VERILOG_OPS[node.op]([source_names[item] for item in node.inputs])
            except KeyError as exc:
                raise ValueError(f"unsupported Verilog operation: {node.op}") from exc
        lines.append(f"  assign {node.node_id} = {expression};")

    lines.append(f"  assign y = {source_names[circuit.output]};")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"
