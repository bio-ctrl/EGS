"""Typed, deterministic Baugh-Wooley bit-heap generation and compositional proof.

The graph manifest is deliberately simple JSON data. The audit reparses emitted
RTL statements and checks graph conservation independently of the reduction
builder's internal column lists.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time


def generate_fused_heap(lanes: int = 4, external_inputs: bool = False):
    if lanes < 1:
        raise ValueError("lanes must be positive")
    width = 10
    columns: list[list[str]] = [[] for _ in range(width)]
    bits: dict[str, dict] = {}
    expr: dict[str, str] = {}
    rtl_expr: dict[str, str] = {}
    lines: list[str] = []

    for lane in range(lanes):
        for i in range(4):
            for j in range(4):
                bit_id = f"pp_{lane}_{i}_{j}"
                inverted = (i == 3) != (j == 3)
                bits[bit_id] = {
                    "id": bit_id, "column": i + j, "kind": "partial_product",
                    "lane": lane, "a_bit": i, "b_bit": j, "inverted": inverted,
                }
                expr[bit_id] = bit_id
                rtl_expr[bit_id] = bit_id
                if not external_inputs:
                    product = f"(a{lane}[{i}] & b{lane}[{j}])"
                    lines.append(
                        f"  wire {bit_id} = " +
                        (f"~{product};" if inverted else f"{product};")
                    )
                columns[i + j].append(bit_id)
        # The 4x4 signed Baugh-Wooley correction is 0x90 modulo 2^8.
        # Sign extension to the 10-bit accumulator adds bits 8 and 9:
        # 0x90 + 0x300 = 0x390, placed at weights 4, 7, 8, and 9.
        for bit in (4, 7, 8, 9):
            bit_id = f"bias_{lane}_{bit}"
            bits[bit_id] = {
                "id": bit_id, "column": bit, "kind": "constant",
                "lane": lane, "value": 1,
            }
            expr[bit_id] = "1'b1"
            rtl_expr[bit_id] = "1'b1"
            columns[bit].append(bit_id)

    compressors = []
    fa_index = 0
    for column in range(width):
        while len(columns[column]) > 2:
            inputs = columns[column][:3]
            del columns[column][:3]
            sum_id = f"fa_s_{fa_index}"
            carry_id = f"fa_c_{fa_index}" if column < width - 1 else None
            compressors.append({
                "id": f"fa_{fa_index}", "kind": "full_adder",
                "column": column, "inputs": inputs, "sum": sum_id,
                "carry": carry_id,
                "carry_column": column + 1 if carry_id else None,
                "carry_truncated_modulo_2_10": carry_id is None,
            })
            bits[sum_id] = {
                "id": sum_id, "column": column, "kind": "compressor_sum",
                "compressor": f"fa_{fa_index}",
            }
            expr[sum_id] = sum_id
            rtl_expr[sum_id] = sum_id
            a, b, c = (expr[item] for item in inputs)
            lines.append(f"  wire {sum_id} = {a} ^ {b} ^ {c};")
            columns[column].append(sum_id)
            if carry_id:
                bits[carry_id] = {
                    "id": carry_id, "column": column + 1,
                    "kind": "compressor_carry", "compressor": f"fa_{fa_index}",
                }
                expr[carry_id] = carry_id
                rtl_expr[carry_id] = carry_id
                lines.append(
                    f"  wire {carry_id} = ({a} & {b}) | ({a} & {c}) | ({b} & {c});"
                )
                columns[column + 1].append(carry_id)
            fa_index += 1

    rows = [
        [columns[k][0] if len(columns[k]) > 0 else None for k in range(width)],
        [columns[k][1] if len(columns[k]) > 1 else None for k in range(width)],
    ]
    row_expr = [
        [expr[item] if item else "1'b0" for item in row] for row in rows
    ]
    lines.append(
        "  wire [9:0] fused_row0 = {" +
        ", ".join(reversed(row_expr[0])) + "};"
    )
    lines.append(
        "  wire [9:0] fused_row1 = {" +
        ", ".join(reversed(row_expr[1])) + "};"
    )
    lines.append("  assign y = fused_row0 + fused_row1;")

    manifest = {
        "schema": "orcus-typed-bit-heap-v1",
        "lanes": lanes,
        "width": width,
        "arithmetic": "modulo-2^10",
        "lane_baugh_wooley_bias": "0x390 per lane",
        "initial_bits": [item for item in bits.values() if item["kind"] in ("partial_product", "constant")],
        "compressors": compressors,
        "final_rows": rows,
        "truncated_top_carries": [
            item["id"] for item in compressors if item["carry_truncated_modulo_2_10"]
        ],
        "final_adder": {"kind": "carry_propagate", "lhs": "fused_row0",
                        "rhs": "fused_row1", "output": "y", "width": 10},
    }
    return lines, manifest


def audit_fused_heap(lines: list[str], manifest: dict) -> dict:
    """Independently validate emitted wire equations and weighted graph flow."""
    source = "\n".join(lines)
    if manifest.get("schema") != "orcus-typed-bit-heap-v1" or manifest.get("width") != 10:
        raise ValueError("unsupported heap manifest schema/width")
    width = manifest["width"]
    bits = {item["id"]: item for item in manifest["initial_bits"]}
    if len(bits) != len(manifest["initial_bits"]):
        raise ValueError("duplicate initial bit IDs")
    expected_ids = {f"pp_{lane}_{i}_{j}" for lane in range(manifest["lanes"]) for i in range(4) for j in range(4)}
    expected_ids |= {f"bias_{lane}_{bit}" for lane in range(manifest["lanes"]) for bit in (4, 7, 8, 9)}
    if set(bits) != expected_ids:
        raise ValueError("initial bit set is incomplete, duplicated, or contains non-source nodes")

    declarations = {}
    for name, rhs in re.findall(r"(?m)^\s*wire\s+(\w+)\s*=\s*(.*);\s*$", source):
        if name in declarations:
            raise ValueError(f"duplicate RTL declaration: {name}")
        declarations[name] = rhs.strip()

    for bit_id, bit in bits.items():
        if bit["kind"] == "partial_product":
            lane, i, j = bit["lane"], bit["a_bit"], bit["b_bit"]
            product = f"(a{lane}[{i}] & b{lane}[{j}])"
            expected = f"~{product}" if bit["inverted"] else product
            if declarations.get(bit_id) != expected:
                raise ValueError(f"Baugh-Wooley polarity/source mismatch: {bit_id}")
            if bit["column"] != i + j:
                raise ValueError(f"partial-product weight mismatch: {bit_id}")
        elif bit["kind"] == "constant":
            if bit["value"] != 1 or bit["column"] not in (4, 7, 8, 9):
                raise ValueError(f"invalid Baugh-Wooley bias bit: {bit_id}")
        else:
            raise ValueError(f"unexpected initial bit kind: {bit['kind']}")

    def rtl_token(bit_id: str) -> str:
        bit = bits.get(bit_id)
        return "1'b1" if bit and bit["kind"] == "constant" else bit_id

    consumers = {bit_id: 0 for bit_id in bits}
    generated = {}
    for node in manifest["compressors"]:
        column = node["column"]
        if node["kind"] != "full_adder" or len(node["inputs"]) != 3:
            raise ValueError("unsupported compressor node")
        for item in node["inputs"]:
            if item not in bits and item not in generated:
                raise ValueError(f"compressor references missing bit: {item}")
            if (bits.get(item) or generated[item])["column"] != column:
                raise ValueError(f"compressor input has wrong weight: {item}")
            consumers[item] = consumers.get(item, 0) + 1
        a, b, c = (rtl_token(item) for item in node["inputs"])
        expected_sum = f"{a} ^ {b} ^ {c}"
        expected_carry = f"({a} & {b}) | ({a} & {c}) | ({b} & {c})"
        if declarations.get(node["sum"]) != expected_sum:
            raise ValueError(f"full-adder sum equation mismatch: {node['id']}")
        generated[node["sum"]] = {"column": column, "kind": "sum"}
        carry = node["carry"]
        if column == width - 1:
            if carry is not None or node["carry_column"] is not None:
                raise ValueError("top-column carry must be explicitly truncated modulo 2^10")
            if not node["carry_truncated_modulo_2_10"]:
                raise ValueError("top-column truncation is not documented")
        else:
            if carry is None or node["carry_column"] != column + 1:
                raise ValueError(f"compressor carry weight must be column {column + 1}")
            if declarations.get(carry) != expected_carry:
                raise ValueError(f"full-adder carry equation mismatch: {node['id']}")
            generated[carry] = {"column": column + 1, "kind": "carry"}

    row_names = ("fused_row0", "fused_row1")
    for row_index, row_name in enumerate(row_names):
        row = manifest["final_rows"][row_index]
        if len(row) != width:
            raise ValueError("final row has incorrect width")
        row_tokens = []
        for column, bit_id in enumerate(row):
            if bit_id is None:
                row_tokens.append("1'b0")
                continue
            bit = bits.get(bit_id) or generated.get(bit_id)
            if bit is None or bit["column"] != column:
                raise ValueError(f"final row bit has wrong weight: {bit_id}")
            consumers[bit_id] = consumers.get(bit_id, 0) + 1
            row_tokens.append(rtl_token(bit_id))
        expected = "{" + ", ".join(reversed(row_tokens)) + "}"
        if declarations.get(row_name) != expected:
            raise ValueError(f"final row RTL wiring mismatch: {row_name}")

    for bit_id, count in consumers.items():
        if count != 1:
            raise ValueError(f"heap bit must have exactly one consumer: {bit_id} ({count})")
    for bit_id in generated:
        if consumers.get(bit_id, 0) != 1:
            raise ValueError(f"dangling/duplicated compressor output: {bit_id}")
    if "assign y = fused_row0 + fused_row1;" not in source:
        raise ValueError("final 10-bit CPA output connection is incorrect")
    expected_bias = sum(1 << item["column"] for item in bits.values()
                        if item["kind"] == "constant")
    if expected_bias != manifest["lanes"] * 0x390:
        raise ValueError("constant bias placement does not equal lanes * 0x390 modulo 2^10")
    return {
        "status": "pass",
        "initial_bits": len(bits),
        "compressors": len(manifest["compressors"]),
        "top_carries_truncated_modulo_2_10": len(manifest["truncated_top_carries"]),
        "final_rows": 2,
        "graph_audit": "all weighted bits conserved; no dangling or multiply-consumed bits",
    }


def _sat_lemma(yosys: str, source: str, top: str, label: str, timeout: int = 30):
    with tempfile.TemporaryDirectory(prefix="orcus-lemma-") as tmp:
        path = Path(tmp) / "lemma.v"
        path.write_text(source)
        script = f"read_verilog {path}; prep -top {top}; sat -verify -prove bad 0"
        started = time.perf_counter()
        result = subprocess.run([yosys, "-p", script], text=True,
                                capture_output=True, timeout=timeout)
        elapsed = time.perf_counter() - started
        output = result.stdout + result.stderr
        if result.returncode != 0 or "SUCCESS" not in output:
            raise RuntimeError(f"{label} SAT lemma failed: {output[-4000:]}")
        return {"result": "PASS", "runtime_seconds": elapsed,
                "log_tail": output[-1200:]}


def _lane_lemma_source():
    lines = ["module lane_lemma(input [3:0] a, input [3:0] b, output bad);"]
    terms = []
    for i in range(4):
        for j in range(4):
            name = f"pp_{i}_{j}"
            product = f"(a[{i}] & b[{j}])"
            expr = f"~{product}" if ((i == 3) != (j == 3)) else product
            lines.append(f"wire {name} = {expr};")
            term = f"term_{i}_{j}"
            lines.append(f"wire [9:0] {term} = {{9'b0, {name}}} << {i+j};")
            terms.append(term)
    lines += [
        "wire [9:0] bw = " + " + ".join(terms + ["10'h390"]) + ";",
        "wire signed [7:0] product8 = $signed(a) * $signed(b);",
        "wire signed [9:0] reference10 = {{2{product8[7]}}, product8};",
        "assign bad = (bw != reference10);",
        "endmodule",
    ]
    return "\n".join(lines) + "\n"


def _primitive_lemma_source(kind: str):
    if kind == "full_adder":
        inputs = "input x0, input x1, input x2"
        rhs = "{2'b0,x0} + {2'b0,x1} + {2'b0,x2}"
        logic = "assign s = x0 ^ x1 ^ x2; assign c = (x0 & x1) | (x0 & x2) | (x1 & x2);"
    else:
        inputs = "input x0, input x1"
        rhs = "{2'b0,x0} + {2'b0,x1}"
        logic = "assign s = x0 ^ x1; assign c = x0 & x1;"
    return (
        f"module primitive_lemma({inputs}, output bad); "
        "wire s, c; " + logic +
        "wire [2:0] weighted = {1'b0,c,1'b0} + {2'b0,s}; "
        f"wire [2:0] expected = {rhs}; "
        "assign bad = (weighted != expected); endmodule\n"
    )


def _cpa_lemma_source():
    return """module cpa_lemma(input [9:0] row0, input [9:0] row1, output bad);
wire [9:0] emitted = row0 + row1;
wire [10:0] full_precision = {1'b0,row0} + {1'b0,row1};
wire [9:0] modulo_reference = full_precision[9:0];
assign bad = (emitted != modulo_reference);
endmodule
"""


def run_compositional_proofs(candidate_source: str, yosys: str):
    lines, manifest = generate_fused_heap(4, external_inputs=False)
    audit_started = time.perf_counter()
    audit = audit_fused_heap(lines, manifest)
    # Ensure the RTL under benchmark is the exact emitted heap that was audited.
    if any(line not in candidate_source for line in lines):
        raise ValueError("benchmark candidate RTL differs from audited typed-heap emission")
    audit["runtime_seconds"] = time.perf_counter() - audit_started

    proof_started = time.perf_counter()
    lemmas = {
        "baugh_wooley_lane_10bit": _sat_lemma(
            yosys, _lane_lemma_source(), "lane_lemma", "10-bit Baugh-Wooley lane identity"),
        "full_adder_weighted_sum": _sat_lemma(
            yosys, _primitive_lemma_source("full_adder"), "primitive_lemma", "full-adder invariant"),
        "half_adder_weighted_sum": _sat_lemma(
            yosys, _primitive_lemma_source("half_adder"), "primitive_lemma", "half-adder invariant"),
        "final_cpa_modulo_2_10": _sat_lemma(
            yosys, _cpa_lemma_source(), "cpa_lemma", "10-bit CPA modulo equivalence"),
    }
    elapsed = time.perf_counter() - proof_started
    return {
        "formal_equivalence": "formal-pass",
        "proof_method": (
            "Compositional Yosys SAT: 10-bit signed Baugh-Wooley lane identity; "
            "full-adder and half-adder weighted-sum lemmas; 10-bit modulo CPA lemma; "
            "independent typed-heap RTL/graph weight-conservation audit."
        ),
        "formal_equivalence_seconds": elapsed,
        "proof_stage_timings_seconds": {
            key: value["runtime_seconds"] for key, value in lemmas.items()
        },
        "proof_lemmas": lemmas,
        "heap_audit": audit,
        "heap_manifest": manifest,
        "proof_log_tail": "All compositional SAT lemmas and typed heap audit passed.",
    }


def tampered_manifest_carry_weight(manifest: dict) -> dict:
    result = deepcopy(manifest)
    node = next((item for item in result["compressors"] if item["carry"] is not None), None)
    if node is None:
        raise ValueError("no non-truncated carry exists to tamper")
    node["carry_column"] = node["column"]
    return result
