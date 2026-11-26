"""Four-lane signed INT4 dot-product accumulation experiment.

All variants instantiate the same four signed 4x4 multipliers and sign-extend
their 8-bit products to a 10-bit signed accumulator. Only the reduction
network changes. Generic-cell counts and VCD toggle counts are not physical
area, critical-path timing, or power measurements.
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
        # This exact multiplier expression is shared by every architecture.
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


def _run_yosys(candidate_text: str, reference_text: str, top: str, yosys: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="orcus-int4-") as tmp:
        root = Path(tmp)
        candidate = root / "candidate.v"
        reference = root / "reference.v"
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
        synth_script = f"read_verilog {candidate}; hierarchy -top {top}; synth -top {top}; stat"
        synth = subprocess.run([yosys, "-p", synth_script], text=True, capture_output=True)
        if synth.returncode:
            raise RuntimeError(synth.stdout[-2500:] + synth.stderr[-1000:])
        counts = re.findall(r"Number of cells:\s+(\d+)", synth.stdout)
        return {
            "formal_equivalence": "formal-pass",
            "yosys_version": subprocess.run([yosys, "-V"], text=True, capture_output=True).stdout.strip(),
            "generic_cell_count": int(counts[-1]) if counts else None,
            "generic_cell_count_evidence": "Yosys synth/stat; not standard-cell area",
            "proof_log_tail": proof.stdout[-1200:],
        }


def _vcd_toggles(vcd_text: str) -> dict:
    ids = {}
    previous = {}
    toggles = {}
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
            ident = line[1:]
            value = line[0].lower()
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


def simulate_activity(candidate_text: str, top: str, iverilog: str, vvp: str) -> dict:
    tb_ports = []
    regs = []
    connections = []
    for i in range(LANES):
        regs += [f"reg signed [3:0] a{i};", f"reg signed [3:0] b{i};"]
        connections += [f".a{i}(a{i})", f".b{i}(b{i})"]
        tb_ports += [f"a{i}", f"b{i}"]
    tb = [
        "module tb;",
        *regs,
        "wire signed [9:0] y;",
        f"{top} dut({', '.join(connections)}, .y(y));",
        "integer i;",
        "initial begin",
        '  $dumpfile("activity.vcd"); $dumpvars(0, tb);',
        "  for (i = 0; i < 512; i = i + 1) begin",
    ]
    for i in range(LANES):
        tb.append(f"    a{i} = ((i * {i+3} + {i*5+1}) % 16) - 8;")
        tb.append(f"    b{i} = ((i * {i+7} + {i*3+2}) % 16) - 8;")
    tb += ["    #5;", "  end", "  $finish;", "end", "endmodule"]
    with tempfile.TemporaryDirectory(prefix="orcus-vcd-") as tmp:
        root = Path(tmp)
        source = root / "candidate.v"
        testbench = root / "tb.v"
        source.write_text(candidate_text)
        testbench.write_text("\n".join(tb) + "\n")
        compile_result = subprocess.run([iverilog, "-g2012", "-s", "tb", "-o", str(root/"sim"), str(source), str(testbench)],
                                        text=True, capture_output=True)
        if compile_result.returncode:
            raise RuntimeError(compile_result.stdout + compile_result.stderr)
        run_result = subprocess.run([vvp, str(root/"sim")], cwd=root, text=True, capture_output=True)
        if run_result.returncode:
            raise RuntimeError(run_result.stdout + run_result.stderr)
        vcd = (root / "activity.vcd").read_text()
        return {"vectors": 512, "signal_bit_toggles": _vcd_toggles(vcd),
                "activity_evidence": "Icarus Verilog deterministic VCD simulation; toggles are not power"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-tools", action="store_true")
    parser.add_argument("--liberty", type=Path, help="Optional target Liberty for future mapped-cell area flow")
    parser.add_argument("--sta", default="sta", help="OpenSTA executable for optional timing analysis")
    args = parser.parse_args()
    yosys, iverilog, vvp = (shutil.which(x) for x in ("yosys", "iverilog", "vvp"))
    missing = [name for name, path in (("yosys", yosys), ("iverilog", iverilog), ("vvp", vvp)) if not path]
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
            synthesis = _run_yosys(source, reference, top, yosys)
            activity = simulate_activity(source, top, iverilog, vvp)
            results.append({
                "variant": variant,
                "multiplier_contract": "identical signed 4x4 expressions in every module; same p0..p3 and sign extension",
                "synthesis": synthesis,
                "activity": activity,
                "search_runtime_seconds": time.perf_counter() - start,
                "mapped_standard_cell_area": None,
                "critical_path_delay": None,
                "power": None,
                "physical_metrics_status": "not-measured: target Liberty, STA constraints, and power methodology not yet configured",
            })
        report = {
            "schema_version": "orcus-int4-dot-product-v1",
            "workload": {"name": "four-lane signed INT4 dot-product accumulation",
                         "lanes": 4, "multiplicand_width": 4, "multiplier_width": 8,
                         "accumulator_width": 10, "signed": True},
            "baseline": "direct-expression",
            "variants": results,
            "limitations": [
                "Yosys generic cell count is not standard-cell area.",
                "VCD bit toggles are switching activity, not power.",
                "Critical-path delay and mapped standard-cell area are not claimed without a target Liberty and STA flow.",
                "The benchmark isolates reduction topology by keeping multiplier expressions and sign extension identical.",
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
