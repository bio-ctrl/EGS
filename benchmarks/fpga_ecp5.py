"""Reproducible Lattice ECP5 synthesis and place-and-route matrix for ORCUS."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orcus.lane_scaling import accumulator_width, module_source, run_compositional_proofs

TARGET_LANES = (4, 8, 16, 32)
VARIANTS = ("direct", "fused_dadda")
DEVICE = "LFE5U-85F-6BG381C"
PACKAGE = "CABGA381"
SPEED_GRADE = 6
TOP = "orcus_fpga_top"


def build_wrapper_source(lanes: int, variant: str) -> str:
    if lanes not in TARGET_LANES:
        raise ValueError(f"unsupported FPGA lane count: {lanes}")
    if variant not in VARIANTS:
        raise ValueError(f"unsupported FPGA architecture: {variant}")
    width = accumulator_width(lanes)
    core_name = f"orcus_{variant}_{lanes}_core"
    core = module_source(core_name, lanes, variant)
    ports = ["input wire clk"]
    for lane in range(lanes):
        ports.extend((
            f"input wire signed [3:0] a{lane}",
            f"input wire signed [3:0] b{lane}",
        ))
    ports.append(f"output reg signed [{width - 1}:0] y")
    lines = [f"module {TOP}({', '.join(ports)});"]
    for lane in range(lanes):
        lines.append(f"  reg signed [3:0] a{lane}_q;")
        lines.append(f"  reg signed [3:0] b{lane}_q;")
    lines.append(f"  wire signed [{width - 1}:0] core_y;")
    connections = []
    for lane in range(lanes):
        connections.extend((f".a{lane}(a{lane}_q)", f".b{lane}(b{lane}_q)"))
    connections.append(".y(core_y)")
    lines.append(f"  {core_name} core_inst ({', '.join(connections)});")
    lines.append("  always @(posedge clk) begin")
    for lane in range(lanes):
        lines.append(f"    a{lane}_q <= a{lane};")
        lines.append(f"    b{lane}_q <= b{lane};")
    lines.append("    y <= core_y;")
    lines.append("  end")
    lines.append("endmodule")
    return core + "\\n".join(lines) + "\\n"


def parse_yosys_netlist(netlist: dict, top: str = TOP) -> dict:
    modules = netlist.get("modules", {})
    if top not in modules:
        raise ValueError(f"Yosys netlist missing top module {top}")
    cells = modules[top].get("cells", {})
    counts = Counter(cell.get("type", "") for cell in cells.values())
    return {
        "cell_counts": dict(sorted((k, v) for k, v in counts.items() if k)),
        "lut4": counts.get("LUT4", 0),
        "ccu2c": counts.get("CCU2C", 0),
        "carry_stages": 2 * counts.get("CCU2C", 0),
        "flip_flops": counts.get("TRELLIS_FF", 0),
        "pfumx": counts.get("PFUMX", 0),
        "l6mux21": counts.get("L6MUX21", 0),
        "mult18x18d": counts.get("MULT18X18D", 0),
        "trellis_io": counts.get("TRELLIS_IO", 0),
    }


def parse_nextpnr_report(report: dict) -> dict:
    utilization = report.get("utilization")
    fmax = report.get("fmax")
    if not isinstance(utilization, dict) or not isinstance(fmax, dict):
        raise ValueError("nextpnr report is missing utilization or fmax")
    clock = fmax.get("clk")
    if clock is None and len(fmax) == 1:
        clock = next(iter(fmax.values()))
    if not isinstance(clock, dict):
        raise ValueError("nextpnr report is missing the clk timing domain")
    achieved = clock.get("achieved")
    constraint = clock.get("constraint")
    if not isinstance(achieved, (int, float)) or achieved <= 0:
        raise ValueError("nextpnr report has no positive achieved Fmax")
    if not isinstance(constraint, (int, float)) or constraint <= 0:
        raise ValueError("nextpnr report has no positive clock constraint")
    return {
        "clock_domain": "clk",
        "achieved_fmax_mhz": float(achieved),
        "constraint_mhz": float(constraint),
        "timing_met": bool(achieved >= constraint),
        "utilization": utilization,
        "detailed_timing": report.get("critical_paths", report.get("timing", {})),
    }


def _run(command: list[str], log_path: Path, timeout: int) -> float:
    start = time.perf_counter()
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        log_path.write_text(stdout + "\\n" + stderr)
        raise TimeoutError(f"command timed out after {timeout}s: {' '.join(command)}") from exc
    elapsed = time.perf_counter() - start
    log_path.write_text(result.stdout + "\\n" + result.stderr)
    if result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\\n"
            + (result.stdout + result.stderr)[-6000:]
        )
    return elapsed


def _version(binary: str) -> str:
    result = subprocess.run([binary, "--version"], text=True, capture_output=True, check=False)
    value = (result.stdout + result.stderr).strip()
    if not value:
        raise RuntimeError(f"could not read version from {binary}")
    return value.splitlines()[0]


def run_one(yosys: str, nextpnr: str, lanes: int, variant: str,
            outdir: Path, freq_mhz: float, seed: int, timeout: int) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    rtl_path = outdir / "design.v"
    netlist_path = outdir / "synth.json"
    synth_log = outdir / "yosys-synth.log"
    report_path = outdir / "nextpnr-report.json"
    route_log = outdir / "nextpnr.log"
    config_path = outdir / "routed.config"
    source = build_wrapper_source(lanes, variant)
    rtl_path.write_text(source)
    core_name = f"orcus_{variant}_{lanes}_core"
    core_source = module_source(core_name, lanes, variant)
    if variant == "fused_dadda":
        formal_result = run_compositional_proofs(lanes, "dadda", core_source, yosys)
        formal = {
            "status": formal_result["formal_equivalence"],
            "proof_method": formal_result["proof_method"],
            "runtime_seconds": formal_result["formal_equivalence_seconds"],
            "proof_stage_timings_seconds": formal_result["proof_stage_timings_seconds"],
            "heap_audit": formal_result["heap_audit"],
        }
    else:
        formal = {
            "status": "baseline-reference",
            "proof_method": "Direct architecture is the comparison baseline; no reduction proof claimed",
            "runtime_seconds": 0.0,
        }

    synth_script = (
        f'read_verilog "{rtl_path}"; '
        f'synth_ecp5 -top {TOP} -json "{netlist_path}"; '
        "stat"
    )
    synth_seconds = _run([yosys, "-p", synth_script], synth_log, timeout)
    netlist = json.loads(netlist_path.read_text())
    resources = parse_yosys_netlist(netlist, TOP)

    route_command = [
        nextpnr, "--85k", "--package", PACKAGE, "--speed", str(SPEED_GRADE),
        "--freq", str(freq_mhz), "--seed", str(seed),
        "--json", str(netlist_path), "--textcfg", str(config_path),
        "--report", str(report_path), "--detailed-timing-report",
        "--lpf-allow-unconstrained", "--timing-allow-fail",
    ]
    route_seconds = _run(route_command, route_log, timeout)
    route_report = parse_nextpnr_report(json.loads(report_path.read_text()))
    return {
        "lanes": lanes,
        "accumulator_width": accumulator_width(lanes),
        "variant": variant,
        "target": DEVICE,
        "formal": formal,
        "resources": resources,
        "post_route": route_report,
        "stage_timings_seconds": {
            "formal": formal["runtime_seconds"],
            "yosys_synth_ecp5": synth_seconds,
            "nextpnr_place_and_route": route_seconds,
            "total": formal["runtime_seconds"] + synth_seconds + route_seconds,
        },
        "files": {
            "rtl": str(rtl_path.name),
            "yosys_netlist": str(netlist_path.name),
            "yosys_log": str(synth_log.name),
            "nextpnr_report": str(report_path.name),
            "nextpnr_log": str(route_log.name),
            "routed_config": str(config_path.name),
        },
    }


def run_matrix(yosys: str, nextpnr: str, outdir: Path,
               freq_mhz: float = 100.0, seed: int = 1, timeout: int = 900) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    report = {
        "schema_version": "orcus-ecp5-fpga-v1",
        "status": "running",
        "target": {
            "part": DEVICE, "family": "Lattice ECP5", "device_option": "--85k",
            "package": PACKAGE, "speed_grade": SPEED_GRADE,
            "clock_target_mhz": freq_mhz, "seed": seed,
        },
        "tools": {
            "yosys": _version(yosys),
            "nextpnr_ecp5": _version(nextpnr),
            "python": sys.version,
            "platform": platform.platform(),
        },
        "matrix": results,
    }
    output = outdir / "results.json"
    try:
        for lanes in TARGET_LANES:
            for variant in VARIANTS:
                row_dir = outdir / f"{lanes}-lane-{variant}"
                row = run_one(yosys, nextpnr, lanes, variant, row_dir,
                              freq_mhz, seed, timeout)
                results.append(row)
                output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\\n")
        report["status"] = "complete"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\\n")
        raise
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--outdir", type=Path, default=Path("artifacts/orcus-fpga-ecp5"))
    parser.add_argument("--yosys", default="yosys")
    parser.add_argument("--nextpnr", default="nextpnr-ecp5")
    parser.add_argument("--freq", type=float, default=100.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--require-tools", action="store_true")
    args = parser.parse_args()
    yosys = shutil.which(args.yosys)
    nextpnr = shutil.which(args.nextpnr)
    missing = [name for name, path in ((args.yosys, yosys), (args.nextpnr, nextpnr)) if not path]
    if missing and args.require_tools:
        raise RuntimeError("Missing required FPGA tools: " + ", ".join(missing))
    if missing:
        report = {
            "schema_version": "orcus-ecp5-fpga-v1",
            "status": "not-run",
            "missing_tools": missing,
        }
    else:
        report = run_matrix(yosys, nextpnr, args.outdir, args.freq, args.seed, args.timeout)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
