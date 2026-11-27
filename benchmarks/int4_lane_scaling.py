"""Reproducible 8/16/32-lane signed INT4 architecture scaling benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orcus.lane_scaling import (
    TARGET_LANES, accumulator_width, module_source, reference_source,
    run_compositional_proofs, run_yosys_equivalence,
)
from benchmarks.signed_int4_dot_product import run_sta, _vcd_toggles

FORMAL_TIMEOUT = 300
SYNTHESIS_TIMEOUT = 180
MAPPING_TIMEOUT = 180
SIMULATION_TIMEOUT = 90
VARIANTS = ("direct", "carry_save", "fused_linear", "fused_dadda")


def _xorshift_vectors(lanes: int, count: int = 512) -> list[tuple[int, ...]]:
    state = 0xC0FFEE01
    seen = set()
    vectors = []
    attempts = 0
    while len(vectors) < count:
        values = []
        for _ in range(2 * lanes):
            state ^= (state << 13) & 0xFFFFFFFF
            state ^= state >> 17
            state ^= (state << 5) & 0xFFFFFFFF
            state &= 0xFFFFFFFF
            nibble = state & 0xF
            values.append(nibble if nibble < 8 else nibble - 16)
        vector = tuple(values)
        attempts += 1
        if vector not in seen:
            seen.add(vector)
            vectors.append(vector)
        if attempts > count * 100:
            raise RuntimeError("xorshift32 failed to generate enough unique vectors")
    return vectors


def simulate_activity(source: str, top: str, lanes: int, width: int,
                      iverilog: str, vvp: str) -> tuple[dict, str]:
    vectors = _xorshift_vectors(lanes)
    if len(vectors) != 512 or len(set(vectors)) != 512:
        raise RuntimeError("exactly 512 unique vectors are required")
    regs, connections = [], []
    for lane in range(lanes):
        regs.extend((f"reg signed [3:0] a{lane};", f"reg signed [3:0] b{lane};"))
        connections.extend((f".a{lane}(a{lane})", f".b{lane}(b{lane})"))
    tb = [
        "\x60timescale 1ns/1ps",
        "module tb;",
        *regs,
        f"reg signed [{width - 1}:0] expected;",
        f"wire signed [{width - 1}:0] y;",
        f"{top} dut({', '.join(connections)}, .y(y));",
        "initial begin",
        '  $dumpfile("activity.vcd"); $dumpvars(0, tb);',
    ]
    for vector in vectors:
        for lane in range(lanes):
            tb.append(f"  a{lane} = 4'd{vector[2 * lane] & 15};")
            tb.append(f"  b{lane} = 4'd{vector[2 * lane + 1] & 15};")
        expected = sum(vector[2 * lane] * vector[2 * lane + 1] for lane in range(lanes))
        expected_literal = f"-{width}'sd{abs(expected)}" if expected < 0 else f"{width}'sd{expected}"
        tb.append(f"  expected = {expected_literal};")
        tb.append("  #5;")
        tb.append('  if (y !== expected) $fatal(1, "dot-product mismatch");')
    tb += ["  $finish;", "end", "endmodule"]
    with tempfile.TemporaryDirectory(prefix="orcus-scaling-vcd-") as tmp:
        root = Path(tmp)
        src, testbench = root / "candidate.v", root / "tb.v"
        src.write_text(source)
        testbench.write_text("\n".join(tb) + "\n")
        try:
            compiled = subprocess.run(
                [iverilog, "-g2012", "-s", "tb", "-o", str(root / "sim"),
                 str(src), str(testbench)],
                text=True, capture_output=True, timeout=SIMULATION_TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"IVERILOG_COMPILE_TIMEOUT: {top} exceeded {SIMULATION_TIMEOUT}s") from exc
        if compiled.returncode:
            raise RuntimeError("Icarus compile failed: " + compiled.stdout[-2500:] + compiled.stderr[-1000:])
        try:
            simulated = subprocess.run(
                [vvp, str(root / "sim")], cwd=root, text=True, capture_output=True,
                timeout=SIMULATION_TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"IVERILOG_SIMULATION_TIMEOUT: {top} exceeded {SIMULATION_TIMEOUT}s") from exc
        if simulated.returncode:
            raise RuntimeError("Icarus simulation failed: " + simulated.stdout[-2500:] + simulated.stderr[-1000:])
        vcd = (root / "activity.vcd").read_text()
    toggles = _vcd_toggles(vcd)
    toggle_total = sum(toggles.values())
    if toggle_total <= 0:
        raise RuntimeError(f"{top}: VCD contains no nonzero signal activity")
    return ({
        "vectors": len(vectors),
        "unique_vectors": len(set(vectors)),
        "stimulus": "fixed-seed xorshift32, 512 unique operand tuples",
        "signal_bit_toggles": toggles,
        "total_signal_bit_toggles": toggle_total,
        "activity_evidence": "Icarus simulation with per-vector signed arithmetic assertions and VCD",
    }, vcd)


def synthesize_and_map(source: str, top: str, yosys: str,
                       liberty: Path | None) -> tuple[dict, str | None]:
    with tempfile.TemporaryDirectory(prefix="orcus-scaling-synth-") as tmp:
        root = Path(tmp)
        candidate, mapped = root / "candidate.v", root / "mapped.v"
        candidate.write_text(source)
        stages = {}
        start = time.perf_counter()
        generic_script = f"read_verilog {candidate}; hierarchy -top {top}; synth -top {top}; stat"
        try:
            generic = subprocess.run([yosys, "-p", generic_script], text=True,
                                     capture_output=True, timeout=SYNTHESIS_TIMEOUT)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"GENERIC_SYNTH_TIMEOUT: {top} exceeded {SYNTHESIS_TIMEOUT}s") from exc
        stages["generic_synthesis_seconds"] = time.perf_counter() - start
        if generic.returncode:
            raise RuntimeError("Yosys generic synthesis failed: " + generic.stdout[-3000:] + generic.stderr[-1000:])
        counts = re.findall(r"Number of cells:\s+(\d+)", generic.stdout)
        result = {
            "generic_cell_count": int(counts[-1]) if counts else None,
            "generic_synthesis_log_tail": generic.stdout[-1500:],
        }
        mapped_text = None
        if liberty is not None:
            start = time.perf_counter()
            mapping_script = (
                f"read_verilog {candidate}; hierarchy -top {top}; "
                f"synth -top {top} -noabc; abc -liberty {liberty}; "
                f"clean; stat -liberty {liberty}; write_verilog -noattr {mapped}"
            )
            try:
                mapping = subprocess.run([yosys, "-p", mapping_script], text=True,
                                         capture_output=True, timeout=MAPPING_TIMEOUT)
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError(f"LIBERTY_MAPPING_TIMEOUT: {top} exceeded {MAPPING_TIMEOUT}s") from exc
            stages["liberty_mapping_seconds"] = time.perf_counter() - start
            if mapping.returncode or not mapped.is_file():
                raise RuntimeError("Nangate45 mapping failed: " + mapping.stdout[-3000:] + mapping.stderr[-1000:])
            areas = re.findall(r"Chip area for module .*?:\s*([0-9.eE+-]+)", mapping.stdout)
            result.update({
                "mapped_standard_cell_area": float(areas[-1]) if areas else None,
                "mapped_area_unit": "Nangate45 Liberty area units",
                "mapping_library": "Nangate45 typical",
                "mapping_log_tail": mapping.stdout[-1800:],
            })
            mapped_text = mapped.read_text()
        result["stage_timings_seconds"] = stages
        return result, mapped_text


def _formal(candidate: str, reference: str, top: str, variant: str,
            lanes: int, yosys: str) -> dict:
    if variant in ("direct", "carry_save"):
        return run_yosys_equivalence(candidate, reference, top, yosys, FORMAL_TIMEOUT)
    schedule = "linear" if variant == "fused_linear" else "dadda"
    return run_compositional_proofs(lanes, schedule, candidate, yosys)


def run_benchmarks(yosys: str, iverilog: str, vvp: str,
                   liberty: Path | None, sta: str | None) -> dict:
    all_results = []
    for lanes in TARGET_LANES:
        width = accumulator_width(lanes)
        reference = reference_source("reference", lanes)
        for variant in VARIANTS:
            top = f"orcus_{variant}_{lanes}"
            print(f"[ORCUS-SCALING] {lanes} lanes/{width} bits {variant}: formal start", flush=True)
            source = module_source(top, lanes, variant)
            total_start = time.perf_counter()
            formal_start = time.perf_counter()
            proof = _formal(source, reference, top, variant, lanes, yosys)
            formal_seconds = time.perf_counter() - formal_start
            if proof.get("formal_equivalence") != "formal-pass":
                raise RuntimeError(f"{top}: formal proof did not pass")
            print(f"[ORCUS-SCALING] {top}: formal PASS in {formal_seconds:.6f}s", flush=True)

            synthesis, mapped = synthesize_and_map(source, top, yosys, liberty)
            activity_start = time.perf_counter()
            activity, vcd = simulate_activity(source, top, lanes, width, iverilog, vvp)
            activity["simulation_runtime_seconds"] = time.perf_counter() - activity_start
            sta_report = {"status": "not-run"}
            if mapped and liberty and sta:
                sta_start = time.perf_counter()
                sta_report = run_sta(mapped, top, liberty, sta, vcd)
                sta_report["opensta_runtime_seconds"] = time.perf_counter() - sta_start
                if sta_report.get("status") != "completed" or sta_report.get("annotated_pin_activities", 0) <= 0:
                    raise RuntimeError(f"{top}: OpenSTA analysis or VCD annotation failed")
            row = {
                "lanes": lanes, "accumulator_width": width, "variant": variant,
                "formal": proof, "formal_runtime_seconds": formal_seconds,
                "synthesis": synthesis, "activity": activity, "sta": sta_report,
                "total_runtime_seconds": time.perf_counter() - total_start,
            }
            all_results.append(row)
            print(
                f"[ORCUS-SCALING] {top}: complete total={row['total_runtime_seconds']:.3f}s "
                f"area={synthesis.get('mapped_standard_cell_area')} "
                f"delay={sta_report.get('critical_path_delay')} "
                f"power={sta_report.get('power_total_uw')}",
                flush=True,
            )
    return {
        "schema_version": "orcus-int4-lane-scaling-v1",
        "workload": {
            "operation": "sum of signed 4x4 INT4 products",
            "target_lane_counts": list(TARGET_LANES),
            "accumulator_widths": {str(n): accumulator_width(n) for n in TARGET_LANES},
            "signed": True, "arithmetic": "exact signed sum; modulo 2^W implementation",
        },
        "variants": all_results,
        "comparisons": {
            "baseline": "direct",
            "carry_save": "multi-stage 3:2 reduction",
            "fused_linear": "Baugh-Wooley typed heap with linear column reduction",
            "fused_dadda": "Baugh-Wooley typed heap with Dadda target-height scheduling",
        },
        "limitations": [
            "Nangate45 is an open research proxy, not a foundry PDK.",
            "Area, delay, and power are pre-layout estimates without routed parasitics.",
            "OpenSTA power uses Liberty models and annotated RTL VCD activity.",
            "512 vectors are deterministic functional checks; formal proofs are the correctness authority.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-tools", action="store_true")
    parser.add_argument("--require-physical", action="store_true")
    parser.add_argument("--liberty", type=Path)
    parser.add_argument("--sta", default="sta")
    args = parser.parse_args()
    yosys, iverilog, vvp = (shutil.which(name) for name in ("yosys", "iverilog", "vvp"))
    missing = [name for name, value in (("yosys", yosys), ("iverilog", iverilog), ("vvp", vvp)) if not value]
    sta = shutil.which(args.sta)
    if missing and args.require_tools:
        raise RuntimeError("Missing required tools: " + ", ".join(missing))
    if args.require_physical and (not args.liberty or not args.liberty.is_file() or not sta):
        raise RuntimeError("Physical mode requires --liberty and OpenSTA")
    if missing:
        report = {"status": "not-run", "missing_tools": missing}
    else:
        report = run_benchmarks(yosys, iverilog, vvp, args.liberty, sta)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
