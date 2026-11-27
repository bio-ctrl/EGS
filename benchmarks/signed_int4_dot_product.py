"""Four-lane signed INT4 dot-product accumulation experiment.

The five reduction baselines use identical signed 4x4 multipliers. The fused
variant instead expands signed products into Baugh-Wooley partial products and
compresses all four lanes in one 10-bit bit heap before a final carry-propagate
addition. Optional Nangate45 mapping/STA/power is pre-layout research evidence,
not manufacturable silicon PPA.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

from orcus.typed_heap import generate_fused_heap, run_compositional_proofs

LANES = 4
FORMAL_TIMEOUT_SECONDS = 300
SYNTHESIS_TIMEOUT_SECONDS = 120
MAPPING_TIMEOUT_SECONDS = 120
SIMULATION_TIMEOUT_SECONDS = 60
OPENSTA_TIMEOUT_SECONDS = 120
VARIANTS = ("direct", "left_deep", "balanced_01_23", "balanced_02_13", "carry_save", "fused_partial_product")


def _fused_partial_product_lines(external_inputs: bool = False) -> list[str]:
    """Emit RTL from the deterministic typed heap graph."""
    lines, _manifest = generate_fused_heap(LANES, external_inputs=external_inputs)
    return lines


def _baugh_wooley_lane_source(name: str) -> str:
    """One-lane 4x4 signed Baugh-Wooley product, returning the 8-bit product."""
    lines = [
        f"module {name}(input signed [3:0] a, input signed [3:0] b, output signed [7:0] p);"
    ]
    terms = []
    for i in range(4):
        for j in range(4):
            pp = f"pp_{i}_{j}"
            product = f"(a[{i}] & b[{j}])"
            expr = f"~{product}" if ((i == 3) != (j == 3)) else product
            lines.append(f"  wire {pp} = {expr};")
            term = f"term_{i}_{j}"
            lines.append(f"  wire [7:0] {term} = {{7'b0, {pp}}} << {i + j};")
            terms.append(term)
    lines.append("  assign p = " + " + ".join(terms + ["8'h90"]) + ";")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def _baugh_wooley_lane_reference() -> str:
    return (
        "module reference(input signed [3:0] a, input signed [3:0] b, "
        "output signed [7:0] p);\n"
        "  assign p = $signed(a) * $signed(b);\n"
        "endmodule\n"
    )


def _fused_heap_gate_source(name: str, tamper: bool = False) -> str:
    ports = ", ".join(
        f"input pp_{lane}_{i}_{j}"
        for lane in range(LANES) for i in range(4) for j in range(4)
    )
    lines = [f"module {name}({ports}, output [9:0] y);"]
    lines.extend(_fused_partial_product_lines(external_inputs=True))
    if tamper:
        lines[-1] = "  assign y = (fused_row0 + fused_row1) ^ 10'b0000000001;"
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def _fused_heap_reference_source() -> str:
    ports = ", ".join(
        f"input pp_{lane}_{i}_{j}"
        for lane in range(LANES) for i in range(4) for j in range(4)
    )
    lines = [f"module reference({ports}, output [9:0] y);"]
    terms = []
    for lane in range(LANES):
        for i in range(4):
            for j in range(4):
                term = f"term_{lane}_{i}_{j}"
                pp = f"pp_{lane}_{i}_{j}"
                lines.append(f"  wire [9:0] {term} = {{9'b0, {pp}}} << {i + j};")
                terms.append(term)
        terms.append("10'h390")
    lines.append("  assign y = " + " + ".join(terms) + ";")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def _run_abc_cec(candidate_text: str, reference_text: str, top: str,
                   yosys: str, abc: str,
                   timeout_seconds: int = FORMAL_TIMEOUT_SECONDS) -> dict:
    """Run full PI/PO combinational equivalence with Berkeley ABC CEC."""
    with tempfile.TemporaryDirectory(prefix="orcus-abc-cec-") as tmp:
        root = Path(tmp)
        candidate = root / "candidate.v"
        reference = root / "reference.v"
        candidate_aig = root / "candidate.aig"
        reference_aig = root / "reference.aig"
        candidate.write_text(candidate_text)
        reference.write_text(reference_text)

        def export_aig(source: Path, module: str, output: Path) -> str:
            script = (
                f"read_verilog {source}; hierarchy -top {module}; "
                "proc; flatten; techmap; opt; aigmap; "
                f"write_aiger -symbols {output}"
            )
            try:
                result = subprocess.run(
                    [yosys, "-p", script], text=True, capture_output=True,
                    timeout=min(timeout_seconds, 60),
                )
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError(
                    f"AIG_EXPORT_TIMEOUT: Yosys AIGER export exceeded "
                    f"{min(timeout_seconds, 60)}s for {module}."
                ) from exc
            if result.returncode or not output.is_file():
                raise RuntimeError(
                    f"Yosys AIGER export failed for {module}: "
                    + result.stdout[-2500:] + result.stderr[-1200:]
                )
            return result.stdout[-1000:]

        started = time.perf_counter()
        ref_log = export_aig(reference, "reference", reference_aig)
        gate_log = export_aig(candidate, top, candidate_aig)
        command = f'cec -T {timeout_seconds} "{reference_aig}" "{candidate_aig}"'
        try:
            result = subprocess.run(
                [abc, "-c", command], text=True, capture_output=True,
                timeout=timeout_seconds + 10,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - started
            raise TimeoutError(
                f"ABC_CEC_TIMEOUT: ABC cec exceeded {timeout_seconds}s for {top}; "
                f"elapsed={elapsed:.2f}s."
            ) from exc
        elapsed = time.perf_counter() - started
        output = result.stdout + result.stderr
        if "Networks are equivalent" in output:
            status = "formal-pass"
        elif "Networks are NOT EQUIVALENT" in output or "Disproved" in output:
            raise RuntimeError("ABC CEC: Networks are NOT EQUIVALENT. " + output[-3500:])
        elif result.returncode:
            raise RuntimeError("ABC CEC exited unsuccessfully: " + output[-3500:])
        else:
            raise RuntimeError("ABC CEC returned no affirmative equivalence verdict: " + output[-3500:])
        return {
            "formal_equivalence": status,
            "proof_method": (
                "Yosys proc/flatten/techmap/opt/aigmap/write_aiger -ascii -symbols; "
                "Berkeley ABC cec on complete reference/candidate AIGER networks; "
                "all primary inputs and all 10 primary outputs compared."
            ),
            "formal_equivalence_seconds": elapsed,
            "proof_log_tail": (
                "REFERENCE AIG EXPORT:\\n" + ref_log +
                "\\nCANDIDATE AIG EXPORT:\\n" + gate_log +
                "\\nABC CEC:\\n" + output[-3000:]
            ),
        }


def module_source(name: str, variant: str) -> str:
    ports = ", ".join(f"input signed [3:0] a{i}, input signed [3:0] b{i}" for i in range(LANES))
    lines = [f"module {name}({ports}, output signed [9:0] y);"]
    if variant == "fused_partial_product":
        lines.extend(_fused_partial_product_lines())
        lines.append("endmodule")
        return "\n".join(lines) + "\n"
    for i in range(LANES):
        lines.append(f"  wire signed [7:0] p{i} = $signed(a{i}) * $signed(b{i});")
        lines.append(f"  wire signed [9:0] e{i} = {{{{2{{p{i}[7]}}}}, p{i}}};")
    if variant == "direct":
        lines.append("  assign y = e0 + e1 + e2 + e3;")
    elif variant == "left_deep":
        lines += ["  wire signed [9:0] r0 = e0 + e1;",
                  "  wire signed [9:0] r1 = r0 + e2;",
                  "  assign y = r1 + e3;"]
    elif variant == "balanced_01_23":
        lines += ["  wire signed [9:0] r0 = e0 + e1;",
                  "  wire signed [9:0] r1 = e2 + e3;",
                  "  assign y = r0 + r1;"]
    elif variant == "balanced_02_13":
        lines += ["  wire signed [9:0] r0 = e0 + e2;",
                  "  wire signed [9:0] r1 = e1 + e3;",
                  "  assign y = r0 + r1;"]
    elif variant == "carry_save":
        lines += [
            "  wire [9:0] s0 = e0 ^ e1 ^ e2;",
            "  wire [9:0] c0 = ((e0 & e1) | (e0 & e2) | (e1 & e2)) << 1;",
            "  wire [9:0] s1 = s0 ^ c0 ^ e3;",
            "  wire [9:0] c1 = ((s0 & c0) | (s0 & e3) | (c0 & e3)) << 1;",
            "  assign y = s1 + c1;",
        ]
    else:
        raise ValueError(variant)
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def _run_equivalence(candidate_text: str, reference_text: str, top: str,
                      yosys: str, timeout_seconds: int = FORMAL_TIMEOUT_SECONDS,
                      use_structural: bool = True) -> dict:
    """Prove all output bits with Yosys' partitioned equivalence flow.

    equiv_make creates a gold/gate equivalence design; equiv_struct matches
    structurally corresponding cells; equiv_simple discharges the remaining
    output-bit partitions with SAT; equiv_status -assert fails closed if any
    partition remains unproven. This checks the complete module output, not a
    sampled input set or a hand-selected subset of bits.
    """
    with tempfile.TemporaryDirectory(prefix="orcus-equiv-") as tmp:
        root = Path(tmp)
        candidate = root / "candidate.v"
        reference = root / "reference.v"
        candidate.write_text(candidate_text)
        reference.write_text(reference_text)
        structural_step = "equiv_struct -icells; " if use_structural else ""
        proof_script = (
            f"read_verilog {reference} {candidate}; "
            "proc; "
            f"equiv_make reference {top} equiv; "
            "hierarchy -top equiv; "
            "clean -purge; "
            + structural_step
            + "equiv_simple -v; "
            + "equiv_status -assert"
        )
        started = time.perf_counter()
        try:
            proof = subprocess.run(
                [yosys, "-p", proof_script], text=True, capture_output=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - started
            raise TimeoutError(
                f"FORMAL_EQUIV_TIMEOUT: Yosys partitioned equivalence exceeded "
                f"{timeout_seconds}s for {top}; elapsed={elapsed:.2f}s. "
                f"Method: equiv_make; {'equiv_struct -icells; ' if use_structural else ''}equiv_simple -v; equiv_status -assert."
            ) from exc
        elapsed = time.perf_counter() - started
        if proof.returncode:
            raise RuntimeError(
                "Yosys partitioned equivalence failed or found an inequivalent output: "
                + proof.stdout[-3500:] + proof.stderr[-1500:]
            )
        if "Equivalence successfully proven" not in proof.stdout and "Equivalence successfully proven!" not in proof.stdout:
            # equiv_status -assert is the fail-closed authority; this guard
            # makes an unexpected Yosys output format visible for review.
            if "Unproven" in proof.stdout or "unproven" in proof.stdout.lower():
                raise RuntimeError("Yosys left equivalence partitions unproven: " + proof.stdout[-3500:])
        return {
            "formal_equivalence": "formal-pass",
            "proof_method": (
                "Yosys equiv_make reference candidate equiv; hierarchy -top equiv; "
                "clean -purge; " + ("equiv_struct -icells; " if use_structural else "") +
                "equiv_simple -v; equiv_status -assert"
            ),
            "formal_equivalence_seconds": elapsed,
            "proof_log_tail": proof.stdout[-1800:],
        }


def _run_yosys(candidate_text: str, reference_text: str, top: str,
               yosys: str, liberty: Path | None = None) -> dict:
    with tempfile.TemporaryDirectory(prefix="orcus-int4-") as tmp:
        root = Path(tmp)
        candidate = root / "candidate.v"
        mapped = root / "mapped.v"
        candidate.write_text(candidate_text)
        stage_timings = {}
        print(f"[ORCUS] {top}: partitioned formal equivalence starting (timeout={FORMAL_TIMEOUT_SECONDS}s)", flush=True)
        stage_start = time.perf_counter()
        if top == "orcus_fused_partial_product":
            proof = run_compositional_proofs(candidate_text, yosys)
        else:
            proof = _run_equivalence(candidate_text, reference_text, top, yosys)
        stage_timings["formal_equivalence_seconds"] = time.perf_counter() - stage_start
        print(f"[ORCUS] {top}: partitioned formal equivalence finished in {stage_timings['formal_equivalence_seconds']:.2f}s", flush=True)

        generic_script = f"read_verilog {candidate}; hierarchy -top {top}; synth -top {top}; stat"
        print(f"[ORCUS] {top}: generic synthesis starting (timeout={SYNTHESIS_TIMEOUT_SECONDS}s)", flush=True)
        stage_start = time.perf_counter()
        try:
            generic = subprocess.run(
                [yosys, "-p", generic_script], text=True, capture_output=True,
                timeout=SYNTHESIS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - stage_start
            raise TimeoutError(
                f"SYNTHESIS_TIMEOUT: Yosys generic synthesis exceeded {SYNTHESIS_TIMEOUT_SECONDS}s "
                f"for {top}; elapsed={elapsed:.2f}s."
            ) from exc
        stage_timings["generic_synthesis_seconds"] = time.perf_counter() - stage_start
        print(f"[ORCUS] {top}: generic synthesis finished in {stage_timings['generic_synthesis_seconds']:.2f}s", flush=True)
        if generic.returncode:
            raise RuntimeError(generic.stdout[-2500:] + generic.stderr[-1000:])
        counts = re.findall(r"Number of cells:\s+(\d+)", generic.stdout)

        mapped_area = None
        mapped_text = None
        mapping_log = None
        if liberty is not None:
            mapped_script = (
                f"read_verilog {candidate}; hierarchy -top {top}; "
                f"synth -top {top} -noabc; abc -liberty {liberty}; "
                f"clean; stat -liberty {liberty}; write_verilog -noattr {mapped}"
            )
            print(f"[ORCUS] {top}: Nangate45 mapping starting (timeout={MAPPING_TIMEOUT_SECONDS}s)", flush=True)
            stage_start = time.perf_counter()
            try:
                mapping = subprocess.run(
                    [yosys, "-p", mapped_script], text=True, capture_output=True,
                    timeout=MAPPING_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired as exc:
                elapsed = time.perf_counter() - stage_start
                raise TimeoutError(
                    f"MAPPING_TIMEOUT: Yosys/ABC Liberty mapping exceeded {MAPPING_TIMEOUT_SECONDS}s "
                    f"for {top}; elapsed={elapsed:.2f}s."
                ) from exc
            stage_timings["liberty_mapping_seconds"] = time.perf_counter() - stage_start
            print(f"[ORCUS] {top}: Nangate45 mapping finished in {stage_timings['liberty_mapping_seconds']:.2f}s", flush=True)
            if mapping.returncode or not mapped.exists():
                raise RuntimeError("Liberty mapping failed: " + mapping.stdout[-2500:] + mapping.stderr[-1000:])
            areas = re.findall(r"Chip area for module .*?:\s*([0-9.eE+-]+)", mapping.stdout)
            mapped_area = float(areas[-1]) if areas else None
            mapped_text = mapped.read_text()
            mapping_log = mapping.stdout[-2500:]

        return {
            "formal_equivalence": proof["formal_equivalence"],
            "proof_method": proof["proof_method"],
            "stage_timings_seconds": stage_timings,
            "yosys_version": subprocess.run([yosys, "-V"], text=True, capture_output=True).stdout.strip(),
            "generic_cell_count": int(counts[-1]) if counts else None,
            "generic_cell_count_evidence": "Yosys synth/stat; not standard-cell area",
            "mapped_standard_cell_area": mapped_area,
            "mapped_area_unit": "library-defined area units from Liberty cell area attributes",
            "mapping_library": "Nangate45 typical" if liberty else None,
            "mapping_log_tail": mapping_log,
            "mapped_verilog": mapped_text,
            "proof_log_tail": proof["proof_log_tail"],
            "proof_stage_timings_seconds": proof.get("proof_stage_timings_seconds"),
            "proof_lemmas": proof.get("proof_lemmas"),
            "heap_audit": proof.get("heap_audit"),
            "heap_manifest": proof.get("heap_manifest"),
        }


def _vcd_toggles(vcd_text: str) -> dict:
    ids, previous, toggles = {}, {}, {}
    in_values = False
    for line in vcd_text.splitlines():
        line = line.strip()
        if line.startswith("$var"):
            parts = line.split()
            if len(parts) >= 5:
                ids[parts[3]] = parts[4]
        elif line.startswith("$enddefinitions"):
            in_values = True
        elif in_values and line and line[0] in "bB":
            parts = line.split()
            if len(parts) == 2:
                value, ident = parts
                value = value[1:].lower()
                if set(value) <= {"0", "1"}:
                    old = previous.get(ident)
                    if old is not None:
                        width = max(len(old), len(value))
                        a, b = old.zfill(width), value.zfill(width)
                        toggles[ident] = toggles.get(ident, 0) + sum(x != y for x, y in zip(a, b))
                    previous[ident] = value
        elif in_values and line and line[0] in "01xzXZ":
            ident, value = line[1:], line[0].lower()
            if value in {"0", "1"}:
                old = previous.get(ident)
                if old is not None:
                    toggles[ident] = toggles.get(ident, 0) + int(old != value)
                previous[ident] = value
    by_name = {}
    for ident, count in toggles.items():
        name = ids.get(ident, ident)
        by_name[name] = by_name.get(name, 0) + count
    return by_name


def simulate_activity(candidate_text: str, top: str, iverilog: str, vvp: str) -> tuple[dict, str]:
    regs, connections = [], []
    for i in range(LANES):
        regs += [f"reg signed [3:0] a{i};", f"reg signed [3:0] b{i};"]
        connections += [f".a{i}(a{i})", f".b{i}(b{i})"]
    # Fixed-seed xorshift32 stimulus: 512 distinct, reproducible 8-input vectors.
    state = 0xC0FFEE01
    vectors = []
    for _ in range(512):
        vector = []
        for _lane in range(LANES):
            pair = []
            for _operand in range(2):
                state ^= (state << 13) & 0xFFFFFFFF
                state ^= state >> 17
                state ^= (state << 5) & 0xFFFFFFFF
                state &= 0xFFFFFFFF
                value = state & 0xF
                pair.append(value if value < 8 else value - 16)
            vector.extend(pair)
        vectors.append(tuple(vector))
    if len(vectors) != 512 or len(set(vectors)) != 512:
        raise RuntimeError(f"Expected 512 unique xorshift32 vectors; got {len(set(vectors))}/{len(vectors)}")
    tb = [
        "`timescale 1ns/1ps",
        "module tb;", *regs, "wire signed [9:0] y;",
        f"{top} dut({', '.join(connections)}, .y(y));",
        "initial begin",
        '  $dumpfile("activity.vcd"); $dumpvars(0, tb);',
    ]
    for vector in vectors:
        for lane in range(LANES):
            tb.append(f"  a{lane} = 4\'d{vector[2 * lane] & 15};")
            tb.append(f"  b{lane} = 4\'d{vector[2 * lane + 1] & 15};")
        tb.append("  #5;")
    tb += ["  $finish;", "end", "endmodule"]
    with tempfile.TemporaryDirectory(prefix="orcus-vcd-") as tmp:
        root = Path(tmp)
        source, testbench = root / "candidate.v", root / "tb.v"
        source.write_text(candidate_text)
        testbench.write_text("\n".join(tb) + "\n")
        try:
            compile_result = subprocess.run(
                [iverilog, "-g2012", "-s", "tb", "-o", str(root/"sim"), str(source), str(testbench)],
                text=True, capture_output=True, timeout=SIMULATION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(
                f"IVERILOG_COMPILE_TIMEOUT: testbench compilation exceeded {SIMULATION_TIMEOUT_SECONDS}s for {top}."
            ) from exc
        if compile_result.returncode:
            raise RuntimeError(compile_result.stdout + compile_result.stderr)
        try:
            run_result = subprocess.run(
                [vvp, str(root/"sim")], cwd=root, text=True, capture_output=True,
                timeout=SIMULATION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(
                f"IVERILOG_SIMULATION_TIMEOUT: VCD simulation exceeded {SIMULATION_TIMEOUT_SECONDS}s for {top}."
            ) from exc
        if run_result.returncode:
            raise RuntimeError(run_result.stdout + run_result.stderr)
        vcd = (root / "activity.vcd").read_text()
        return ({
            "vectors": len(vectors),
            "unique_vectors": len(set(vectors)),
            "stimulus": "fixed-seed xorshift32; 512 reproducible vectors",
            "signal_bit_toggles": _vcd_toggles(vcd),
            "activity_evidence": "Icarus Verilog deterministic RTL VCD; switching activity, not power",
        }, vcd)


def _parse_opensta_power_report(report: str) -> dict:
    """Parse the total OpenSTA power row and explicit VCD annotation count.

    report_power's table is in Watts even when report_units displays a smaller
    power unit. Convert each component to microWatts for the benchmark schema.
    """
    power_match = re.search(
        r"(?m)^Total\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+[-+0-9.eE]+%?\s*$",
        report,
    )
    if not power_match or "(Watts)" not in report:
        raise RuntimeError("OpenSTA report_power total row or Watts unit missing")
    internal_w, switching_w, leakage_w, total_w = (float(value) for value in power_match.groups())
    annotation = re.search(r"(?m)^Annotated\s+(\d+)\s+pin activities\.", report)
    if not annotation or int(annotation.group(1)) <= 0:
        raise RuntimeError("OpenSTA did not confirm VCD pin activity annotation")
    scale = 1_000_000.0
    return {
        "power_internal_uw": internal_w * scale,
        "power_switching_uw": switching_w * scale,
        "power_leakage_uw": leakage_w * scale,
        "power_total_uw": total_w * scale,
        "power_source_unit": "W from OpenSTA report_power table; structured fields converted to µW",
        "annotated_pin_activities": int(annotation.group(1)),
        "raw_power_components_w": {
            "internal": internal_w,
            "switching": switching_w,
            "leakage": leakage_w,
            "total": total_w,
        },
    }


def run_sta(mapped_verilog: str, top: str, liberty: Path, sta: str, vcd_text: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="orcus-sta-") as tmp:
        root = Path(tmp)
        netlist, vcd, script = root/"mapped.v", root/"activity.vcd", root/"run.tcl"
        netlist.write_text(mapped_verilog)
        vcd.write_text(vcd_text)
        tcl = [
            f'read_liberty "{liberty}"',
            f'read_verilog "{netlist}"',
            f"link_design {top}",
            "create_clock -name virtual_clock -period 10",
            "set_input_delay -clock virtual_clock 0 [all_inputs]",
            "set_output_delay -clock virtual_clock 0 [all_outputs]",
            "set_input_transition 0.05 [all_inputs]",
            "set_load 0.01 [all_outputs]",
            f'read_vcd -scope tb/dut "{vcd}"',
            "report_units",
            "report_checks -path_delay max -from [all_inputs] -to [all_outputs] -format full",
            "report_power -digits 6",
        ]
        script.write_text("\n".join(tcl) + "\n")
        try:
            result = subprocess.run(
                [sta, "-no_splash", "-exit", str(script)], text=True, capture_output=True,
                timeout=OPENSTA_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(
                f"OPENSTA_TIMEOUT: timing/power analysis exceeded {OPENSTA_TIMEOUT_SECONDS}s for {top}."
            ) from exc
        if result.returncode or re.search(r"(?m)^Error:", result.stdout):
            raise RuntimeError("OpenSTA analysis failed: " + result.stdout[-5000:] + result.stderr[-1000:])
        # The first data-arrival line is the actual path delay; OpenSTA repeats
        # its negated value later when calculating slack. Do not read that second line.
        timing = re.findall(r"(?im)^\s*([-+0-9.eE]+)\s+data arrival time\b", result.stdout)
        if not timing:
            raise RuntimeError("OpenSTA did not report a numeric constrained data-arrival time; report tail:\n" + result.stdout[-7000:])
        power = _parse_opensta_power_report(result.stdout)
        return {
            "status": "completed",
            "critical_path_delay": float(timing[0]),
            "critical_path_delay_unit": "ns (OpenSTA report_units)",
            **power,
            "power_method": "OpenSTA Liberty power models with RTL VCD input activity; pre-layout, no parasitics",
            "sta_version": subprocess.run([sta, "-version"], text=True, capture_output=True).stdout.strip(),
            "raw_report": result.stdout[-7000:],
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-tools", action="store_true")
    parser.add_argument("--require-physical", action="store_true")
    parser.add_argument("--liberty", type=Path, help="Target Liberty file for mapped area, timing, and power estimation")
    parser.add_argument("--sta", default="sta", help="OpenSTA executable")
    args = parser.parse_args()

    yosys, iverilog, vvp = (shutil.which(x) for x in ("yosys", "iverilog", "vvp"))
    missing = [name for name, path in (("yosys", yosys), ("iverilog", iverilog), ("vvp", vvp)) if not path]
    sta = shutil.which(args.sta)
    if args.require_physical and (not args.liberty or not args.liberty.is_file() or not sta):
        raise RuntimeError("Physical-metric mode requires an existing --liberty file and OpenSTA executable")
    if missing and args.require_tools:
        raise RuntimeError("Missing required tools: " + ", ".join(missing))
    if missing:
        report = {"status": "not-run", "missing_tools": missing}
    else:
        reference = module_source("reference", "direct")
        results = []
        for variant in VARIANTS:
            top = f"orcus_{variant}"
            source = module_source(top, variant)
            start = time.perf_counter()
            print(f"[ORCUS] {variant}: starting formal, synthesis, and mapping stages", flush=True)
            synthesis = _run_yosys(source, reference, top, yosys, args.liberty)
            mapped_verilog = synthesis.pop("mapped_verilog")
            print(
                f"[ORCUS] {variant}: Yosys complete; formal={synthesis['formal_equivalence']}; "
                f"generic_cells={synthesis['generic_cell_count']}; mapped_area={synthesis['mapped_standard_cell_area']}",
                flush=True,
            )
            stage_start = time.perf_counter()
            print(f"[ORCUS] {variant}: Icarus simulation starting (timeout={SIMULATION_TIMEOUT_SECONDS}s)", flush=True)
            activity, vcd_text = simulate_activity(source, top, iverilog, vvp)
            activity_seconds = time.perf_counter() - stage_start
            activity["simulation_runtime_seconds"] = activity_seconds
            print(
                f"[ORCUS] {variant}: simulation complete in {activity_seconds:.2f}s; "
                f"vectors={activity['vectors']}; unique={activity['unique_vectors']}",
                flush=True,
            )
            stage_start = time.perf_counter()
            sta_report = (
                run_sta(mapped_verilog, top, args.liberty, sta, vcd_text)
                if mapped_verilog and sta and args.liberty else {"status": "not-run"}
            )
            if sta_report["status"] == "completed":
                sta_report["opensta_runtime_seconds"] = time.perf_counter() - stage_start
            if sta_report["status"] == "completed":
                print(
                    f"[ORCUS] {variant}: OpenSTA complete; delay_ns={sta_report['critical_path_delay']}; "
                    f"power_uw={sta_report['power_total_uw']}; "
                    f"annotated_pins={sta_report['annotated_pin_activities']}",
                    flush=True,
                )
            results.append({
                "variant": variant,
                "multiplier_contract": (
                    "four signed 4x4 products expanded into Baugh-Wooley partial products; "
                    "all lanes share one 10-bit compressor heap"
                    if variant == "fused_partial_product"
                    else "identical signed 4x4 expressions in every module; same p0..p3 and sign extension"
                ),
                "synthesis": synthesis,
                "activity": activity,
                "sta": sta_report,
                "search_and_evaluation_runtime_seconds": time.perf_counter() - start,
                "physical_metrics_status": "pre-layout Nangate45 research-library estimates" if sta_report["status"] == "completed" else "not-measured",
            })
            print(
                f"[ORCUS] {variant}: complete in {time.perf_counter() - start:.2f}s",
                flush=True,
            )
        report = {
            "schema_version": "orcus-int4-dot-product-v2",
            "workload": {"name": "four-lane signed INT4 dot-product accumulation",
                         "lanes": 4, "multiplicand_width": 4, "multiplier_width": 8,
                         "accumulator_width": 10, "signed": True},
            "baseline": "direct-expression",
            "target_library": {
                "name": "Nangate45 typical",
                "purpose": "open research and flow-validation library; not a manufacturable process kit",
                "timing_constraints": {
                    "virtual_clock_period": 10,
                    "input_delay": 0,
                    "output_delay": 0,
                    "input_transition": 0.05,
                    "output_load": 0.01,
                    "parasitics": "not included",
                },
            } if args.liberty else None,
            "variants": results,
            "limitations": [
                "Nangate45 is a research proxy, not a foundry PDK or manufacturable process.",
                "Area, delay, and power are pre-layout Liberty-based estimates with no routed parasitics.",
                "VCD activity is generated from deterministic RTL simulation and annotated onto the mapped design by matching top-level ports.",
                "The four baseline variants isolate reduction topology with identical multiplier expressions; the fused variant expands the same signed products into Baugh-Wooley partial products and combines all lanes in one bit heap.",
                "No FPGA or silicon measurements are claimed.",
            ],
        }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())