"""Parameterized signed INT4 dot-product architectures and compositional proofs.

The accumulator width is chosen from the requested lane count. Fused heaps are
represented as typed weighted bits and compressor nodes, then audited from the
emitted RTL and manifest rather than trusting the generator's working columns.
"""
from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import re
import subprocess
import tempfile
import time


TARGET_LANES = (8, 16, 32)
SCHEDULES = ("linear", "dadda")


def accumulator_width(lanes: int) -> int:
    if lanes not in (4, *TARGET_LANES):
        raise ValueError(f"supported scaling targets are {TARGET_LANES}, got {lanes}")
    return 8 + math.ceil(math.log2(lanes))


def baugh_wooley_bias(width: int) -> int:
    if width < 8:
        raise ValueError("accumulator width must be at least 8")
    return (1 << width) - 112


def _bias_columns(width: int) -> list[int]:
    bias = baugh_wooley_bias(width)
    return [column for column in range(width) if (bias >> column) & 1]


def _compress(columns, bits, expressions, nodes, lines, column, width,
              stage, kind):
    arity = 3 if kind == "full_adder" else 2
    inputs = columns[column][:arity]
    del columns[column][:arity]
    index = len(nodes)
    prefix = "fa" if kind == "full_adder" else "ha"
    node_id = f"{prefix}_{index}"
    sum_id = f"{prefix}_s_{index}"
    carry_id = f"{prefix}_c_{index}" if column < width - 1 else None
    tokens = [expressions[item] for item in inputs]
    if kind == "full_adder":
        a, b, c = tokens
        sum_expr = f"{a} ^ {b} ^ {c}"
        carry_expr = f"({a} & {b}) | ({a} & {c}) | ({b} & {c})"
    else:
        a, b = tokens
        sum_expr = f"{a} ^ {b}"
        carry_expr = f"{a} & {b}"
    node = {
        "id": node_id, "kind": kind, "column": column, "stage": stage,
        "inputs": inputs, "sum": sum_id, "carry": carry_id,
        "carry_column": column + 1 if carry_id else None,
        "carry_truncated_modulo_2_W": carry_id is None,
    }
    nodes.append(node)
    bits[sum_id] = {"id": sum_id, "column": column,
                    "kind": "compressor_sum", "compressor": node_id}
    expressions[sum_id] = sum_id
    lines.append(f"  wire {sum_id} = {sum_expr};")
    columns[column].append(sum_id)
    if carry_id:
        bits[carry_id] = {"id": carry_id, "column": column + 1,
                          "kind": "compressor_carry", "compressor": node_id}
        expressions[carry_id] = carry_id
        lines.append(f"  wire {carry_id} = {carry_expr};")
        columns[column + 1].append(carry_id)


def generate_fused_heap(lanes: int, schedule: str = "linear"):
    width = accumulator_width(lanes)
    if schedule not in SCHEDULES:
        raise ValueError(f"schedule must be one of {SCHEDULES}")
    columns: list[list[str]] = [[] for _ in range(width)]
    bits: dict[str, dict] = {}
    expressions: dict[str, str] = {}
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
                product = f"(a{lane}[{i}] & b{lane}[{j}])"
                expression = f"~{product}" if inverted else product
                expressions[bit_id] = bit_id
                lines.append(f"  wire {bit_id} = {expression};")
                columns[i + j].append(bit_id)
        # raw complemented matrix = signed product + 112.
        # Add 2^W - 112 so the result is signed product modulo 2^W.
        for bit in _bias_columns(width):
            bit_id = f"bias_{lane}_{bit}"
            bits[bit_id] = {
                "id": bit_id, "column": bit, "kind": "constant",
                "lane": lane, "value": 1,
            }
            expressions[bit_id] = "1'b1"
            columns[bit].append(bit_id)

    nodes = []
    stage_targets = []
    if schedule == "linear":
        for column in range(width):
            while len(columns[column]) > 2:
                _compress(columns, bits, expressions, nodes, lines,
                          column, width, 0, "full_adder")
    else:
        maximum = max(map(len, columns))
        targets = [2]
        while targets[-1] < maximum:
            targets.append((3 * targets[-1]) // 2)
        stage_targets = list(reversed(targets[:-1]))
        for stage, target in enumerate(stage_targets):
            # Stage outputs are held for the next stage. Only carries from a
            # lower column in this same stage join the current column's work.
            next_columns: list[list[str]] = [[] for _ in range(width)]
            stage_carries: list[list[str]] = [[] for _ in range(width)]
            for column in range(width):
                work = list(columns[column]) + stage_carries[column]
                while len(work) + len(next_columns[column]) > target:
                    excess = len(work) + len(next_columns[column]) - target
                    kind = "full_adder" if excess >= 2 and len(work) >= 3 else "half_adder"
                    arity = 3 if kind == "full_adder" else 2
                    inputs = work[:arity]
                    del work[:arity]
                    index = len(nodes)
                    prefix = "fa" if kind == "full_adder" else "ha"
                    node_id = f"{prefix}_{index}"
                    sum_id = f"{prefix}_s_{index}"
                    carry_id = f"{prefix}_c_{index}" if column < width - 1 else None
                    tokens = [expressions[item] for item in inputs]
                    if kind == "full_adder":
                        a, b, c = tokens
                        sum_expr = f"{a} ^ {b} ^ {c}"
                        carry_expr = f"({a} & {b}) | ({a} & {c}) | ({b} & {c})"
                    else:
                        a, b = tokens
                        sum_expr = f"{a} ^ {b}"
                        carry_expr = f"{a} & {b}"
                    nodes.append({
                        "id": node_id, "kind": kind, "column": column, "stage": stage,
                        "inputs": inputs, "sum": sum_id, "carry": carry_id,
                        "carry_column": column + 1 if carry_id else None,
                        "carry_truncated_modulo_2_W": carry_id is None,
                    })
                    bits[sum_id] = {"id": sum_id, "column": column,
                                    "kind": "compressor_sum", "compressor": node_id}
                    expressions[sum_id] = sum_id
                    lines.append(f"  wire {sum_id} = {sum_expr};")
                    next_columns[column].append(sum_id)
                    if carry_id:
                        bits[carry_id] = {"id": carry_id, "column": column + 1,
                                          "kind": "compressor_carry", "compressor": node_id}
                        expressions[carry_id] = carry_id
                        lines.append(f"  wire {carry_id} = {carry_expr};")
                        stage_carries[column + 1].append(carry_id)
                next_columns[column].extend(work)
            columns = next_columns

    if any(len(column) > 2 for column in columns):
        raise RuntimeError("compressor schedule did not reduce every column to at most two bits")

    rows = [
        [columns[column][0] if len(columns[column]) > 0 else None for column in range(width)],
        [columns[column][1] if len(columns[column]) > 1 else None for column in range(width)],
    ]
    for row_index, row in enumerate(rows):
        row_expr = [expressions[item] if item else "1'b0" for item in row]
        lines.append(
            f"  wire [{width - 1}:0] fused_row{row_index} = {{"
            + ", ".join(reversed(row_expr)) + "};"
        )
    lines.append("  assign y = fused_row0 + fused_row1;")

    manifest = {
        "schema": "orcus-scaled-typed-bit-heap-v1",
        "lanes": lanes,
        "width": width,
        "arithmetic": f"modulo-2^{width}",
        "schedule": schedule,
        "stage_targets": stage_targets,
        "lane_baugh_wooley_bias": hex(baugh_wooley_bias(width)),
        "initial_bits": [item for item in bits.values() if item["kind"] in ("partial_product", "constant")],
        "compressors": nodes,
        "final_rows": rows,
        "truncated_top_carries": [
            node["id"] for node in nodes if node["carry_truncated_modulo_2_W"]
        ],
        "final_adder": {
            "kind": "carry_propagate", "lhs": "fused_row0",
            "rhs": "fused_row1", "output": "y", "width": width,
        },
    }
    return lines, manifest


def audit_fused_heap(lines: list[str], manifest: dict) -> dict:
    """Reparse emitted RTL and independently check every weighted graph edge."""
    width = manifest.get("width")
    lanes = manifest.get("lanes")
    if manifest.get("schema") != "orcus-scaled-typed-bit-heap-v1":
        raise ValueError("unsupported typed heap schema")
    if width != accumulator_width(lanes):
        raise ValueError("accumulator width does not match lane-count contract")
    if manifest.get("schedule") not in SCHEDULES:
        raise ValueError("unknown compressor schedule")
    bits_list = manifest.get("initial_bits", [])
    bits = {item["id"]: item for item in bits_list}
    if len(bits) != len(bits_list):
        raise ValueError("duplicate initial bit IDs")
    expected_ids = {
        f"pp_{lane}_{i}_{j}" for lane in range(lanes)
        for i in range(4) for j in range(4)
    }
    expected_ids |= {
        f"bias_{lane}_{column}" for lane in range(lanes)
        for column in _bias_columns(width)
    }
    if set(bits) != expected_ids:
        raise ValueError("initial bit set is incomplete or contains unexpected nodes")

    source = "\n".join(lines)
    declarations = {}
    for name, rhs in re.findall(
        r"(?m)^\s*wire(?:\s+\[[^\]]+\])?\s+(\w+)\s*=\s*(.*);\s*$", source
    ):
        if name in declarations:
            raise ValueError(f"duplicate RTL declaration: {name}")
        declarations[name] = rhs.strip()

    for bit_id, bit in bits.items():
        if bit["kind"] == "partial_product":
            lane, i, j = bit["lane"], bit["a_bit"], bit["b_bit"]
            if bit["column"] != i + j:
                raise ValueError(f"partial-product weight mismatch: {bit_id}")
            product = f"(a{lane}[{i}] & b{lane}[{j}])"
            expected = f"~{product}" if bit["inverted"] else product
            if declarations.get(bit_id) != expected:
                raise ValueError(f"Baugh-Wooley polarity/source mismatch: {bit_id}")
        elif bit["kind"] == "constant":
            if bit["value"] != 1 or bit["column"] not in _bias_columns(width):
                raise ValueError(f"invalid bias bit: {bit_id}")
        else:
            raise ValueError(f"unexpected source-bit kind: {bit['kind']}")

    consumers = {bit_id: 0 for bit_id in bits}
    generated = {}
    expected_generated_declarations = set()
    for node in manifest["compressors"]:
        column = node["column"]
        kind = node["kind"]
        arity = 3 if kind == "full_adder" else 2 if kind == "half_adder" else 0
        if not arity or len(node["inputs"]) != arity:
            raise ValueError(f"invalid compressor arity: {node['id']}")
        for bit_id in node["inputs"]:
            if bit_id not in bits and bit_id not in generated:
                raise ValueError(f"compressor references missing bit: {bit_id}")
            source_bit = bits.get(bit_id) or generated[bit_id]
            if source_bit["column"] != column:
                raise ValueError(f"compressor input has wrong weight: {bit_id}")
            consumers[bit_id] = consumers.get(bit_id, 0) + 1

        def token(bit_id):
            item = bits.get(bit_id)
            return "1'b1" if item and item["kind"] == "constant" else bit_id

        tokens = [token(item) for item in node["inputs"]]
        if kind == "full_adder":
            a, b, c = tokens
            sum_expr = f"{a} ^ {b} ^ {c}"
            carry_expr = f"({a} & {b}) | ({a} & {c}) | ({b} & {c})"
        else:
            a, b = tokens
            sum_expr = f"{a} ^ {b}"
            carry_expr = f"{a} & {b}"
        if declarations.get(node["sum"]) != sum_expr:
            raise ValueError(f"compressor sum equation mismatch: {node['id']}")
        generated[node["sum"]] = {"column": column, "kind": "sum"}
        expected_generated_declarations.add(node["sum"])

        carry = node["carry"]
        if node["carry_truncated_modulo_2_W"] != (column == width - 1):
            raise ValueError("compressor top-column truncation flag is inconsistent")
        if column == width - 1:
            if carry is not None or node["carry_column"] is not None:
                raise ValueError("top-column carry must be explicitly truncated")
            if not node["carry_truncated_modulo_2_W"]:
                raise ValueError("top-column truncation is not documented")
        else:
            if carry is None or node["carry_column"] != column + 1:
                raise ValueError(f"compressor carry must route to column {column + 1}")
            if declarations.get(carry) != carry_expr:
                raise ValueError(f"compressor carry equation mismatch: {node['id']}")
            generated[carry] = {"column": column + 1, "kind": "carry"}
            expected_generated_declarations.add(carry)

    for row_index in range(2):
        row_name = f"fused_row{row_index}"
        row = manifest["final_rows"][row_index]
        if len(row) != width:
            raise ValueError("final row width mismatch")
        row_tokens = []
        for column, bit_id in enumerate(row):
            if bit_id is None:
                row_tokens.append("1'b0")
                continue
            bit = bits.get(bit_id) or generated.get(bit_id)
            if bit is None or bit["column"] != column:
                raise ValueError(f"final row bit has incorrect weight: {bit_id}")
            consumers[bit_id] = consumers.get(bit_id, 0) + 1
            row_tokens.append(token(bit_id))
        expected_row = "{" + ", ".join(reversed(row_tokens)) + "}"
        if declarations.get(row_name) != expected_row:
            raise ValueError(f"final row RTL wiring mismatch: {row_name}")
        expected_generated_declarations.add(row_name)

    for bit_id, count in consumers.items():
        if count != 1:
            raise ValueError(f"bit must have exactly one consumer: {bit_id} ({count})")
    for bit_id in generated:
        if consumers.get(bit_id, 0) != 1:
            raise ValueError(f"dangling or multiply-consumed compressor output: {bit_id}")
    expected_declarations = expected_generated_declarations | {
        bit_id for bit_id, bit in bits.items() if bit["kind"] == "partial_product"
    }
    if set(declarations) != expected_declarations:
        raise ValueError("emitted RTL contains missing or unaccounted wire declarations")
    if "assign y = fused_row0 + fused_row1;" not in source:
        raise ValueError("final modulo-W CPA output connection mismatch")
    bias = sum(1 << item["column"] for item in bits.values() if item["kind"] == "constant")
    if bias % (1 << width) != (lanes * baugh_wooley_bias(width)) % (1 << width):
        raise ValueError("bias bits do not equal lanes times the derived per-lane bias")
    expected_truncations = [
        node["id"] for node in manifest["compressors"]
        if node["column"] == width - 1
    ]
    if sorted(expected_truncations) != sorted(manifest["truncated_top_carries"]):
        raise ValueError("top-column truncation manifest mismatch")
    return {
        "status": "pass", "lanes": lanes, "width": width,
        "initial_bits": len(bits), "compressors": len(manifest["compressors"]),
        "full_adders": sum(n["kind"] == "full_adder" for n in manifest["compressors"]),
        "half_adders": sum(n["kind"] == "half_adder" for n in manifest["compressors"]),
        "truncated_top_carries": len(expected_truncations),
        "graph_audit": "weighted bits conserved; no dangling or multiply-consumed bits",
    }


def module_source(name: str, lanes: int, variant: str, schedule: str = "linear") -> str:
    width = accumulator_width(lanes)
    ports = ", ".join(
        f"input signed [3:0] a{i}, input signed [3:0] b{i}" for i in range(lanes)
    )
    lines = [f"module {name}({ports}, output signed [{width - 1}:0] y);"]
    if variant in ("fused_linear", "fused_dadda"):
        rtl, _ = generate_fused_heap(lanes, "linear" if variant == "fused_linear" else "dadda")
        lines.extend(rtl)
        lines.append("endmodule")
        return "\n".join(lines) + "\n"

    products = []
    for lane in range(lanes):
        lines.append(f"  wire signed [7:0] p{lane} = $signed(a{lane}) * $signed(b{lane});")
        lines.append(
            f"  wire signed [{width - 1}:0] e{lane} = "
            f"{{{{{width - 8}{{p{lane}[7]}}}}, p{lane}}};"
        )
        products.append(f"e{lane}")
    if variant == "direct":
        lines.append("  assign y = " + " + ".join(products) + ";")
    elif variant == "carry_save":
        layer = products
        stage = 0
        while len(layer) > 2:
            next_layer = []
            for offset in range(0, len(layer), 3):
                group = layer[offset:offset + 3]
                if len(group) == 3:
                    a, b, c = group
                    sum_name, carry_name = f"cs_s_{stage}_{offset}", f"cs_c_{stage}_{offset}"
                    lines.append(f"  wire [{width - 1}:0] {sum_name} = {a} ^ {b} ^ {c};")
                    lines.append(
                        f"  wire [{width - 1}:0] {carry_name} = "
                        f"(({a} & {b}) | ({a} & {c}) | ({b} & {c})) << 1;"
                    )
                    next_layer.extend((sum_name, carry_name))
                else:
                    next_layer.extend(group)
            layer = next_layer
            stage += 1
        lines.append(f"  assign y = {layer[0]} + {layer[1]};")
    else:
        raise ValueError(f"unknown architecture variant: {variant}")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def reference_source(name: str, lanes: int) -> str:
    return module_source(name, lanes, "direct")


def _sat_lemma(yosys: str, source: str, top: str, label: str, timeout: int = 60):
    with tempfile.TemporaryDirectory(prefix="orcus-scaled-lemma-") as tmp:
        path = Path(tmp) / "lemma.v"
        path.write_text(source)
        script = f"read_verilog {path}; prep -top {top}; sat -verify -prove bad 0"
        start = time.perf_counter()
        try:
            result = subprocess.run([yosys, "-p", script], text=True,
                                    capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"SAT_TIMEOUT: {label} exceeded {timeout}s") from exc
        elapsed = time.perf_counter() - start
        output = result.stdout + result.stderr
        if result.returncode or "SUCCESS" not in output:
            raise RuntimeError(f"SAT lemma failed ({label}): {output[-3500:]}")
        return {"result": "PASS", "runtime_seconds": elapsed, "log_tail": output[-1000:]}


def _lane_lemma_source(width: int) -> str:
    terms = []
    lines = [f"module lane_lemma(input [3:0] a, input [3:0] b, output bad);"]
    for i in range(4):
        for j in range(4):
            pp = f"pp_{i}_{j}"
            product = f"(a[{i}] & b[{j}])"
            expression = f"~{product}" if ((i == 3) != (j == 3)) else product
            lines.append(f"  wire {pp} = {expression};")
            term = f"term_{i}_{j}"
            lines.append(f"  wire [{width - 1}:0] {term} = {{{width - 1}'b0, {pp}}} << {i + j};")
            terms.append(term)
    bias = baugh_wooley_bias(width)
    lines += [
        f"  wire [{width - 1}:0] bw = " + " + ".join(terms + [f"{width}'h{bias:x}"]) + ";",
        "  wire signed [7:0] product8 = $signed(a) * $signed(b);",
        f"  wire signed [{width - 1}:0] reference = {{{{{width - 8}{{product8[7]}}}}, product8}};",
        "  assign bad = (bw != reference);",
        "endmodule",
    ]
    return "\n".join(lines) + "\n"


def _primitive_lemma_source(kind: str) -> str:
    if kind == "full_adder":
        inputs = "input x0, input x1, input x2"
        rhs = "{2'b0,x0} + {2'b0,x1} + {2'b0,x2}"
        logic = "assign s = x0 ^ x1 ^ x2; assign c = (x0 & x1) | (x0 & x2) | (x1 & x2);"
    else:
        inputs = "input x0, input x1"
        rhs = "{2'b0,x0} + {2'b0,x1}"
        logic = "assign s = x0 ^ x1; assign c = x0 & x1;"
    return (
        f"module primitive_lemma({inputs}, output bad); wire s, c; {logic} "
        "wire [2:0] weighted = {1'b0,c,1'b0} + {2'b0,s}; "
        f"wire [2:0] expected = {rhs}; "
        "assign bad = (weighted != expected); endmodule\n"
    )


def _cpa_lemma_source(width: int) -> str:
    return f"""module cpa_lemma(input [{width - 1}:0] row0, input [{width - 1}:0] row1, output bad);
wire [{width - 1}:0] emitted = row0 + row1;
wire [{width}:0] full_precision = {{1'b0,row0}} + {{1'b0,row1}};
wire [{width - 1}:0] modulo_reference = full_precision[{width - 1}:0];
assign bad = (emitted != modulo_reference);
endmodule
"""


def run_compositional_proofs(lanes: int, schedule: str, candidate_source: str,
                             yosys: str) -> dict:
    width = accumulator_width(lanes)
    rtl, manifest = generate_fused_heap(lanes, schedule)
    audit_start = time.perf_counter()
    audit = audit_fused_heap(rtl, manifest)
    if any(line not in candidate_source for line in rtl):
        raise ValueError("candidate RTL does not contain the exact audited heap emission")
    audit["runtime_seconds"] = time.perf_counter() - audit_start
    proof_start = time.perf_counter()
    lemmas = {
        "baugh_wooley_lane_identity": _sat_lemma(
            yosys, _lane_lemma_source(width), "lane_lemma",
            f"{lanes}-lane target {width}-bit Baugh-Wooley lane identity"),
        "full_adder_weighted_sum": _sat_lemma(
            yosys, _primitive_lemma_source("full_adder"), "primitive_lemma",
            "full-adder invariant"),
        "half_adder_weighted_sum": _sat_lemma(
            yosys, _primitive_lemma_source("half_adder"), "primitive_lemma",
            "half-adder invariant"),
        "final_cpa_modulo_width": _sat_lemma(
            yosys, _cpa_lemma_source(width), "cpa_lemma",
            f"{width}-bit modulo CPA equivalence"),
    }
    return {
        "formal_equivalence": "formal-pass",
        "proof_method": "Yosys SAT lane identity + FA/HA weighted invariants + modulo-W CPA + independent graph audit",
        "formal_equivalence_seconds": time.perf_counter() - proof_start,
        "proof_stage_timings_seconds": {
            key: value["runtime_seconds"] for key, value in lemmas.items()
        },
        "proof_lemmas": lemmas,
        "heap_audit": audit,
        "heap_manifest": manifest,
    }


def _csa_lemma_source(width: int) -> str:
    return f"""module csa_lemma(input [{width - 1}:0] x0, x1, x2, output bad);
wire [{width - 1}:0] sum_bits = x0 ^ x1 ^ x2;
wire [{width - 1}:0] carry_bits = ((x0 & x1) | (x0 & x2) | (x1 & x2)) << 1;
wire [{width - 1}:0] compressed = sum_bits + carry_bits;
wire [{width - 1}:0] reference = x0 + x1 + x2;
assign bad = (compressed != reference);
endmodule
"""


def run_yosys_equivalence(candidate_source: str, reference: str, top: str,
                          yosys: str, timeout: int = 300) -> dict:
    # Carry-save trees are proved compositionally: exact source/tree audit,
    # shared signed lane-product nodes, a universal vector CSA lemma, and the
    # modulo-W final-adder lemma. This avoids an intractable monolithic miter.
    if "carry_save" in top:
        width_match = re.search(r"\[(\d+):0\] y\);", candidate_source)
        module_match = re.search(r"module\s+(\w+)\s*\(", candidate_source)
        reference_match = re.search(r"module\s+(\w+)\s*\(", reference)
        if not width_match or not module_match or not reference_match:
            raise ValueError("carry-save source module/width could not be parsed")
        width = int(width_match.group(1)) + 1
        lanes_match = re.search(r"_carry_save_(\d+)$", top)
        if not lanes_match:
            raise ValueError("carry-save proof top does not encode lane count")
        lanes = int(lanes_match.group(1))
        candidate_top = module_match.group(1)
        reference_top = reference_match.group(1)
        if candidate_top != top:
            raise ValueError("carry-save candidate top name mismatch")
        expected_candidate = module_source(candidate_top, lanes, "carry_save")
        expected_reference = module_source(reference_top, lanes, "direct")
        if candidate_source != expected_candidate or reference != expected_reference:
            raise ValueError("carry-save RTL differs from independently regenerated audited tree")
        for lane in range(lanes):
            product_line = f"  wire signed [7:0] p{lane} = $signed(a{lane}) * $signed(b{lane});"
            extension_line = (
                f"  wire signed [{width - 1}:0] e{lane} = "
                f"{{{{{width - 8}{{p{lane}[7]}}}}, p{lane}}};"
            )
            if product_line not in candidate_source or product_line not in reference:
                raise ValueError(f"shared signed product node missing or changed: lane {lane}")
            if extension_line not in candidate_source or extension_line not in reference:
                raise ValueError(f"shared sign-extension node missing or changed: lane {lane}")
        sum_nodes = re.findall(r"^  wire \[\d+:0\] cs_s_\d+_\d+ =", candidate_source, re.M)
        carry_nodes = re.findall(r"^  wire \[\d+:0\] cs_c_\d+_\d+ =", candidate_source, re.M)
        if not sum_nodes or len(sum_nodes) != len(carry_nodes):
            raise ValueError("carry-save tree has incomplete sum/carry node pairs")
        if "assign y = " not in candidate_source:
            raise ValueError("carry-save tree has no final CPA output")
        proof_start = time.perf_counter()
        csa = _sat_lemma(yosys, _csa_lemma_source(width), "csa_lemma",
                         f"{lanes}-lane {width}-bit vector carry-save invariant")
        cpa = _sat_lemma(yosys, _cpa_lemma_source(width), "cpa_lemma",
                         f"{lanes}-lane {width}-bit final modulo CPA invariant")
        elapsed = time.perf_counter() - proof_start
        return {
            "formal_equivalence": "formal-pass",
            "proof_method": "compositional Yosys SAT: exact regenerated CSA-tree audit + shared signed lane products + vector CSA invariant + modulo-W CPA invariant",
            "formal_equivalence_seconds": elapsed,
            "proof_stage_timings_seconds": {
                "carry_save_vector_invariant": csa["runtime_seconds"],
                "final_cpa_modulo_width": cpa["runtime_seconds"],
            },
            "graph_audit": {
                "status": "pass",
                "lanes": lanes,
                "width": width,
                "sum_nodes": len(sum_nodes),
                "carry_nodes": len(carry_nodes),
                "source_tree_match": True,
            },
            "proof_lemmas": {"carry_save_vector_invariant": csa, "final_cpa_modulo_width": cpa},
        }

    with tempfile.TemporaryDirectory(prefix="orcus-scaled-equiv-") as tmp:
        root = Path(tmp)
        candidate_path, reference_path = root / "candidate.v", root / "reference.v"
        candidate_path.write_text(candidate_source)
        reference_path.write_text(reference)
        script = (
            f"read_verilog {reference_path} {candidate_path}; proc; "
            f"equiv_make reference {top} equiv; hierarchy -top equiv; clean -purge; "
            "equiv_simple -v; equiv_status -assert"
        )
        start = time.perf_counter()
        try:
            result = subprocess.run([yosys, "-p", script], text=True,
                                    capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"YOSYS_EQUIV_TIMEOUT: {top} exceeded {timeout}s") from exc
        elapsed = time.perf_counter() - start
        if result.returncode:
            raise RuntimeError("Yosys equivalence failed: " + result.stdout[-3000:] + result.stderr[-1000:])
        return {
            "formal_equivalence": "formal-pass",
            "proof_method": "Yosys equiv_make + equiv_simple + equiv_status -assert",
            "formal_equivalence_seconds": elapsed,
            "proof_log_tail": result.stdout[-1200:],
        }

def tamper_partial_product_polarity(lines: list[str]) -> list[str]:
    changed = list(lines)
    index = next((i for i, line in enumerate(changed)
                  if "pp_0_3_0" in line and "~(" in line), None)
    if index is None:
        raise ValueError("expected inverted partial-product wire not found")
    changed[index] = changed[index].replace("~(", "(", 1)
    return changed


def tamper_compressor_carry_weight(manifest: dict) -> dict:
    result = deepcopy(manifest)
    node = next((item for item in result["compressors"] if item["carry"] is not None), None)
    if node is None:
        raise ValueError("no non-truncated carry to tamper")
    node["carry_column"] = node["column"]
    return result


def tamper_output_bit(lines: list[str], width: int) -> list[str]:
    changed = list(lines)
    target = "  assign y = fused_row0 + fused_row1;"
    index = changed.index(target)
    changed[index] = f"  assign y = (fused_row0 + fused_row1) ^ {width}'b" + ("0" * (width - 1)) + "1;"
    return changed
