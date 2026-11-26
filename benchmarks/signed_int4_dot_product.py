"""Four-lane signed INT4 dot-product accumulation experiment.

All variants instantiate identical signed 4x4 multipliers and sign-extend
their 8-bit products to a 10-bit signed accumulator. Only reduction topology
changes. Optional Nangate45 mapping/STA/power is pre-layout research evidence,
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

LANES = 4
VARIANTS = ("direct", "left_deep", "balanced_01_23", "balanced_02_13", "carry_save")


def module_source(name: str, variant: str) -> str:
    ports = ", ".join(f"input signed [3:0] a{i}, input signed [3:0] b{i}" for i in range(LANES))
    lines = [f"module {name}({ports}, output signed [9:0] y);"]
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


def _run_yosys(candidate_text: str, reference_text: str, top: str,
               yosys: str, liberty: Path | None = None) -> dict:
    with tempfile.TemporaryDirectory(prefix="orcus-int4-") as tmp:
        root = Path(tmp)
        candidate = root / "candidate.v"
        reference = root / "reference.v"
        mapped = root / "mapped.v"
        candidate.write_text(candidate_text)
        reference.write_text(reference_text)
        proof_script = (
            f"read_verilog {candidate} {reference}; "
            f"proc; miter -equiv -flatten reference {top} m; "
            "sat -verify -prove trigger 0 m"
        )
        proof = subprocess.run([yosys, "-p", proof_script], text=True, capture_output=True)
        if proof.returncode or "SAT proof finished - no model found: SUCCESS!" not in proof.stdout:
            raise RuntimeError("Yosys SAT equivalence failed: " + proof.stdout[-2500:] + proof.stderr[-1000:])

        generic_script = f"read_verilog {candidate}; hierarchy -top {top}; synth -top {top}; stat"
        generic = subprocess.run([yosys, "-p", generic_script], text=True, capture_output=True)
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
            mapping = subprocess.run([yosys, "-p", mapped_script], text=True, capture_output=True)
            if mapping.returncode or not mapped.exists():
                raise RuntimeError("Liberty mapping failed: " + mapping.stdout[-2500:] + mapping.stderr[-1000:])
            areas = re.findall(r"Chip area for module .*?:\s*([0-9.eE+-]+)", mapping.stdout)
            mapped_area = float(areas[-1]) if areas else None
            mapped_text = mapped.read_text()
            mapping_log = mapping.stdout[-2500:]

        return {
            "formal_equivalence": "formal-pass",
            "yosys_version": subprocess.run([yosys, "-V"], text=True, capture_output=True).stdout.strip(),
            "generic_cell_count": int(counts[-1]) if counts else None,
            "generic_cell_count_evidence": "Yosys synth/stat; not standard-cell area",
            "mapped_standard_cell_area": mapped_area,
            "mapped_area_unit": "library-defined area units from Liberty cell area attributes",
            "mapping_library": "Nangate45 typical" if liberty else None,
            "mapping_log_tail": mapping_log,
            "mapped_verilog": mapped_text,
            "proof_log_tail": proof.stdout[-1200:],
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
    tb = [
        "`timescale 1ns/1ps",
        "module tb;", *regs, "wire signed [9:0] y;",
        f"{top} dut({', '.join(connections)}, .y(y));",
        "initial begin",
        '  $dumpfile("activity.vcd"); $dumpvars(0, tb);',
    ]
    for vector in vectors:
        for lane in range(LANES):
            tb.append(f"  a{lane} = 4\'sd{vector[2 * lane]};")
            tb.append(f"  b{lane} = 4\'sd{vector[2 * lane + 1]};")
        tb.append("  #5;")
    tb += ["  $finish;", "end", "endmodule"]
    with tempfile.TemporaryDirectory(prefix="orcus-vcd-") as tmp:
        root = Path(tmp)
        source, testbench = root / "candidate.v", root / "tb.v"
        source.write_text(candidate_text)
        testbench.write_text("\n".join(tb) + "\n")
        compile_result = subprocess.run(
            [iverilog, "-g2012", "-s", "tb", "-o", str(root/"sim"), str(source), str(testbench)],
            text=True, capture_output=True,
        )
        if compile_result.returncode:
            raise RuntimeError(compile_result.stdout + compile_result.stderr)
        run_result = subprocess.run([vvp, str(root/"sim")], cwd=root, text=True, capture_output=True)
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
        result = subprocess.run([sta, "-no_splash", "-exit", str(script)], text=True, capture_output=True)
        if result.returncode or re.search(r"(?m)^Error:", result.stdout):
            raise RuntimeError("OpenSTA analysis failed: " + result.stdout[-5000:] + result.stderr[-1000:])
        # The first data-arrival line is the actual path delay; OpenSTA repeats
        # its negated value later when calculating slack. Do not read that second line.
        timing = re.findall(r"(?im)^\s*([-+0-9.eE]+)\s+data arrival time\b", result.stdout)
        if not timing:
            raise RuntimeError("OpenSTA did not report a numeric constrained data-arrival time; report tail:\n" + result.stdout[-7000:])
        power_rows = re.findall(
            r"^\s*Total\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)",
            result.stdout, re.MULTILINE,
        )
        return {
            "status": "completed",
            "critical_path_delay": float(timing[0]) if timing else None,
            "critical_path_delay_unit": "ns (OpenSTA report_units)",
            "power_total": float(power_rows[-1][3]) if power_rows else None,
            "power_unit": "library-defined power unit; see report_units in raw report",
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
            synthesis = _run_yosys(source, reference, top, yosys, args.liberty)
            mapped_verilog = synthesis.pop("mapped_verilog")
            activity, vcd_text = simulate_activity(source, top, iverilog, vvp)
            sta_report = (
                run_sta(mapped_verilog, top, args.liberty, sta, vcd_text)
                if mapped_verilog and sta and args.liberty else {"status": "not-run"}
            )
            results.append({
                "variant": variant,
                "multiplier_contract": "identical signed 4x4 expressions in every module; same p0..p3 and sign extension",
                "synthesis": synthesis,
                "activity": activity,
                "sta": sta_report,
                "search_and_evaluation_runtime_seconds": time.perf_counter() - start,
                "physical_metrics_status": "pre-layout Nangate45 research-library estimates" if sta_report["status"] == "completed" else "not-measured",
            })
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
                "The benchmark isolates reduction topology by keeping multiplier expressions and sign extension identical.",
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
