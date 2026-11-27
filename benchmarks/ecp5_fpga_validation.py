"""ECP5 place-and-route comparison for ORCUS direct and fused-Dadda MACs."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orcus.lane_scaling import (FPGA_TARGET_LANES, module_source, reference_source,
    run_compositional_proofs, run_yosys_equivalence)

DEVICE = "LFE5U-85F-6BG381C"
PNR_ARGS = ("--85k", "--package", "CABGA381", "--speed", "6")
CLOCK_MHZ = 100.0
ARCHITECTURES = ("direct", "fused_dadda")

def wrapper_source(lanes: int, variant: str):
    width = 8 + (lanes.bit_length() - 1)
    core, top = f"orcus_{variant}_{lanes}_core", f"fpga_{variant}_{lanes}"
    lines = [f"module {top}(input wire clk, output reg signed [{width-1}:0] result);"]
    for i in range(lanes):
        seed = (0xA5 ^ ((i + 1) * 37)) & 255 or (i + 1)
        lines += [f"reg [7:0] rng_{i} = 8'h{seed:02x};",
                  f"wire signed [3:0] a{i} = rng_{i}[3:0];",
                  f"wire signed [3:0] b{i} = rng_{i}[7:4];"]
    ports = ", ".join(x for i in range(lanes) for x in (f".a{i}(a{i})", f".b{i}(b{i})"))
    lines += [f"wire signed [{width-1}:0] core_y;", f"{core} dut({ports}, .y(core_y));",
              "always @(posedge clk) begin"]
    for i in range(lanes):
        lines.append(f"rng_{i} <= {{rng_{i}[6:0], rng_{i}[7] ^ rng_{i}[5] ^ rng_{i}[4] ^ rng_{i}[3]}};")
    lines += ["result <= core_y;", "end", "endmodule"]
    return module_source(core, lanes, variant) + "\n" + "\n".join(lines) + "\n", top, core

def run(cmd, timeout, label):
    try: p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as e: raise TimeoutError(f"{label} timeout after {timeout}s") from e
    out = p.stdout + "\n" + p.stderr
    if p.returncode: raise RuntimeError(f"{label} failed ({p.returncode}):\n{out[-6000:]}")
    return out

def cell_counts(path, top):
    mod = json.loads(path.read_text())["modules"][top]
    counts = {}
    for cell in mod.get("cells", {}).values():
        counts[cell["type"]] = counts.get(cell["type"], 0) + 1
    return counts

def find_fmax(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in ("fmax", "max_frequency", "achieved_frequency"):
                if isinstance(v, (int, float)): return float(v)
                if isinstance(v, dict):
                    for e in v.values():
                        if isinstance(e, (int, float)): return float(e)
                        if isinstance(e, dict):
                            for key in ("achieved", "fmax", "MHz"):
                                if isinstance(e.get(key), (int, float)): return float(e[key])
            got = find_fmax(v)
            if got is not None: return got
    if isinstance(obj, list):
        for v in obj:
            got = find_fmax(v)
            if got is not None: return got
    return None

def utilization(report):
    for key in ("utilization", "utilisation"):
        u = report.get(key)
        if isinstance(u, dict):
            out = {k: (v.get("used", v.get("count")) if isinstance(v, dict) else v)
                   for k, v in u.items()}
            if out: return out
    raise RuntimeError("nextpnr JSON lacks utilization/utilisation data")

def run_matrix(yosys, nextpnr):
    rows = []
    versions = {"yosys": run([yosys, "-V"], 30, "Yosys version").strip(),
                "nextpnr_ecp5": run([nextpnr, "--version"], 30, "nextpnr version").strip()}
    for lanes in FPGA_TARGET_LANES:
        width = 8 + (lanes.bit_length() - 1)
        ref = reference_source("reference", lanes)
        for arch in ARCHITECTURES:
            source, top, core = wrapper_source(lanes, arch)
            core_source = module_source(core, lanes, arch)
            if arch == "direct":
                proof = run_yosys_equivalence(core_source, ref, core, yosys, timeout=180)
            else:
                proof = run_compositional_proofs(lanes, "dadda", core_source, yosys)
            if proof.get("formal_equivalence") != "formal-pass":
                raise RuntimeError(f"{top}: formal proof did not pass")
            print(f"[ORCUS-ECP5] {top}: formal PASS", flush=True)
            with tempfile.TemporaryDirectory(prefix="orcus-ecp5-") as tmp:
                root = Path(tmp); rtl = root/"design.v"; net = root/"design.json"
                cfg = root/"design.config"; rpt = root/"report.json"
                rtl.write_text(source)
                yosys_script = f"read_verilog -sv {rtl}; hierarchy -top {top}; synth_ecp5 -top {top} -json {net}; stat"
                synth_log = run([yosys, "-p", yosys_script], 300, f"Yosys synth_ecp5 {top}")
                cells = cell_counts(net, top)
                pnr_cmd = [nextpnr, *PNR_ARGS, "--json", str(net), "--textcfg", str(cfg),
                           "--freq", str(CLOCK_MHZ), "--report", str(rpt), "--lpf-allow-unconstrained"]
                pnr_log = run(pnr_cmd, 900, f"nextpnr ECP5 P&R {top}")
                if not cfg.is_file() or not rpt.is_file(): raise RuntimeError(f"{top}: missing P&R outputs")
                report = json.loads(rpt.read_text()); util = utilization(report)
                fmax = find_fmax(report)
                if fmax is None:
                    found = re.findall(r"Max frequency for clock .*?:\s*([0-9.]+)\s*MHz", pnr_log)
                    if found: fmax = float(found[-1])
                if fmax is None: raise RuntimeError(f"{top}: post-route Fmax not found")
                rows.append({
                    "device": DEVICE, "family": "Lattice ECP5", "lanes": lanes,
                    "accumulator_width": width, "architecture": arch, "formal": proof,
                    "lut4_comb_cells": util.get("TRELLIS_COMB"),
                    "carry_resources": {"CCU2C_yosys_netlist": cells.get("CCU2C", 0),
                                        "TRELLIS_ALU54B": util.get("TRELLIS_ALU54B")},
                    "flip_flops": util.get("TRELLIS_FF"), "utilization": util,
                    "post_route_fmax_mhz": fmax, "clock_constraint_mhz": CLOCK_MHZ,
                    "yosys_cell_counts": cells, "tool_versions": versions,
                    "yosys_log_tail": synth_log[-2000:], "nextpnr_log_tail": pnr_log[-4000:],
                })
                print(f"[ORCUS-ECP5] {top}: P&R complete LUT4={util.get('TRELLIS_COMB')} "
                      f"FF={util.get('TRELLIS_FF')} Fmax={fmax}MHz", flush=True)
    return {"schema_version":"orcus-ecp5-validation-v1", "device":DEVICE,
            "nextpnr_args":list(PNR_ARGS), "clock_constraint_mhz":CLOCK_MHZ,
            "architectures":list(ARCHITECTURES), "tool_versions":versions, "results":rows,
            "limitations":["ECP5 P&R results are device-specific, not ASIC PPA.",
             "Top-level clock/output pins are not board-pin constrained.",
             "Independent per-lane LFSR stimulus and output register are included in resource totals."]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--require-tools", action="store_true")
    args=ap.parse_args()
    yosys, nextpnr = shutil.which("yosys"), shutil.which("nextpnr-ecp5")
    missing=[n for n,p in (("yosys",yosys),("nextpnr-ecp5",nextpnr)) if not p]
    if missing and args.require_tools: raise RuntimeError("Missing FPGA tools: "+", ".join(missing))
    report=run_matrix(yosys,nextpnr) if not missing else {"status":"not-run","missing_tools":missing}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
