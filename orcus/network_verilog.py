"""Verilog emitter for multi-output ORCUS network DAGs."""

from __future__ import annotations

import re

from .network import CircuitNetwork


_OPS = {
    "NOT": lambda a: f"~{a[0]}",
    "AND": lambda a: f"({a[0]} & {a[1]})",
    "OR": lambda a: f"({a[0]} | {a[1]})",
    "XOR": lambda a: f"({a[0]} ^ {a[1]})",
    "NAND": lambda a: f"~({a[0]} & {a[1]})",
    "NOR": lambda a: f"~({a[0]} | {a[1]})",
    "XNOR": lambda a: f"~({a[0]} ^ {a[1]})",
}


def emit_network_verilog(network: CircuitNetwork, module_name: str = "orcus_network") -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", module_name):
        raise ValueError("module_name must be a valid Verilog identifier")
    for output_name, _ in network.outputs:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", output_name):
            raise ValueError(f"invalid output identifier: {output_name}")

    input_ports = [f"x{i}" for i in range(network.input_count)]
    output_names = [name for name, _ in network.outputs]
    if set(input_ports) & set(output_names):
        raise ValueError("output names cannot collide with input port names")
    ports = input_ports + output_names
    source_names: dict[str, str] = {}
    for node in network.nodes:
        if node.op == "VAR":
            assert node.value is not None
            if not 0 <= node.value < network.input_count:
                raise ValueError(f"invalid variable index on {node.node_id}")
            source_names[node.node_id] = f"x{node.value}"
        else:
            source_names[node.node_id] = node.node_id

    lines = [f"module {module_name}({', '.join(ports)});", f"  input {', '.join(f'x{i}' for i in range(network.input_count))};"]
    lines.append(f"  output {', '.join(name for name, _ in network.outputs)};")
    for node in network.nodes:
        if node.op != "VAR":
            lines.append(f"  wire {node.node_id};")
    for node in network.nodes:
        if node.op == "VAR":
            continue
        if node.op == "CONST":
            expression = f"1'b{int(bool(node.value))}"
        else:
            try:
                expression = _OPS[node.op]([source_names[source] for source in node.inputs])
            except KeyError as exc:
                raise ValueError(f"unsupported gate: {node.op}") from exc
        lines.append(f"  assign {node.node_id} = {expression};")
    for name, node_id in network.outputs:
        lines.append(f"  assign {name} = {source_names[node_id]};")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"
