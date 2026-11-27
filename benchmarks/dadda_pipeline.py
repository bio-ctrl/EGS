"""Sequential formal and 512-transaction streaming validation for pipelined Dadda RTL."""
from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from orcus.dadda_pipeline import generate_dadda_pipelined
from orcus.lane_scaling import module_source, accumulator_width

LANES = (4, 8, 16, 32)
VECTOR_COUNT = 512
SEED = 0x0C0FFEE


def _ports(lanes: int) -> tuple[list[str], list[str]]:
    decls, conns = [], []
    for lane in range(lanes):
        decls.extend((f"input wire signed [3:0] a{lane}", f"input wire signed [3:0] b{lane}"))
        conns.extend((f".a{lane}(a{lane})", f".b{lane}(b{lane})"))
    return decls, conns


def build_sequential_miter(lanes: int) -> tuple[str, int]:
    design = generate_dadda_pipelined(lanes)
    width, latency = design.width, design.latency
    decls, conns = _ports(lanes)
    ref = module_source(f"orcus_pipeline_reference_{lanes}", lanes, "direct")
    top_ports = ["input wire clk", "input wire reset", "input wire in_valid"] + decls + ["output wire bad"]
    dut_conns = [".clk(clk)", ".reset(reset)", ".in_valid(in_valid)",
                 ".out_valid(dut_valid)", ".out_data(dut_data)"] + conns
    ref_conns = conns + [".y(ref_data)"]
    lines = [ref, design.source, f"module orcus_pipeline_miter_{lanes}({', '.join(top_ports)});",
             f"  wire signed [{width - 1}:0] ref_data;",
             f"  wire signed [{width - 1}:0] dut_data;",
             "  wire dut_valid;"]
    lines.append(f"  orcus_dadda_pipelined_{lanes} dut ({', '.join(dut_conns)});")
    lines.append(f"  orcus_pipeline_reference_{lanes} ref ({', '.join(ref_conns)});")
    lines.append(f"  reg [{width - 1}:0] ref_data_pipe [0:{latency}];")
    lines.append(f"  reg [{latency}:0] ref_valid_pipe;")
    lines.append("  integer k;")
    lines.append("  always @(posedge clk) begin")
    lines.append("    if (reset) begin")
    lines.append(f"      ref_valid_pipe <= {{{latency + 1}{{1'b0}}}};")
    lines.append(f"      for (k = 0; k <= {latency}; k = k + 1) ref_data_pipe[k] <= {{{width}{{1'b0}}}};")
    lines.append("    end else begin")
    lines.append("      ref_data_pipe[0] <= ref_data;")
    lines.append("      ref_valid_pipe[0] <= in_valid;")
    lines.append(f"      for (k = 1; k <= {latency}; k = k + 1) begin")
    lines.append("        ref_data_pipe[k] <= ref_data_pipe[k-1];")
    lines.append("        ref_valid_pipe[k] <= ref_valid_pipe[k-1];")
    lines.append("      end")
    lines.append("    end")
    lines.append("  end")
    lines.append(f"  assign bad = (dut_valid != ref_valid_pipe[{latency}]) ||")
    lines.append(f"               (dut_valid && (dut_data != ref_data_pipe[{latency}]));")
    lines.append("endmodule")
    return "\n".join(lines) + "\n", latency


def _signed4(value: int) -> int:
    value &= 15
    return value - 16 if value & 8 else value


def _sv_signed(value: int, width: int) -> str:
    return f"-{width}'sd{-value}" if value < 0 else f"{width}'sd{value}"


def _vectors(lanes: int, count: int = VECTOR_COUNT) -> list[tuple[list[int], list[int], int]]:
    rng = random.Random(SEED + lanes)
    width = accumulator_width(lanes)
    mask = (1 << width) - 1
    result = []
    for _ in range(count):
        a = [rng.randrange(16) for _ in range(lanes)]
        b = [rng.randrange(16) for _ in range(lanes)]
        total = sum(_signed4(x) * _signed4(y) for x, y in zip(a, b)) & mask
        if total & (1 << (width - 1)):
            total -= 1 << width
        result.append((a, b, total))
    return result


def build_streaming_testbench(lanes: int) -> tuple[str, int]:
    design = generate_dadda_pipelined(lanes)
    width, latency = design.width, design.latency
    vectors = _vectors(lanes)
    ports = [".clk(clk)", ".reset(reset)", ".in_valid(in_valid)", ".out_valid(out_valid)", ".out_data(out_data)"]
    for lane in range(lanes):
        ports.extend((f".a{lane}(a{lane})", f".b{lane}(b{lane})"))
    lines = [design.source, "module tb;", "  reg clk=0;", "  reg reset=1;", "  reg in_valid=0;",
             "  wire out_valid;", f"  wire signed [{width - 1}:0] out_data;"]
    for lane in range(lanes):
        lines.extend((f"  reg signed [3:0] a{lane}=0;", f"  reg signed [3:0] b{lane}=0;"))
    lines.append(f"  orcus_dadda_pipelined_{lanes} dut ({', '.join(ports)});")
    lines.append("  always #5 clk = ~clk;")
    lines.append("  integer idx;")
    lines.append("  initial begin")
    lines.append("    repeat (2) @(negedge clk); reset = 0;")
    for idx, (a, b, expected) in enumerate(vectors):
        lines.append("    @(negedge clk); in_valid = 1'b1;")
        for lane in range(lanes):
            lines.append(f"    a{lane} = {_sv_signed(_signed4(a[lane]), 4)}; b{lane} = {_sv_signed(_signed4(b[lane]), 4)};")
        lines.append("    @(posedge clk); #1;")
        if idx >= latency:
            exp = vectors[idx - latency][2]
            lines.append(f"    if (out_valid !== 1'b1 || out_data !== {_sv_signed(exp, width)}) $fatal(1, \"stream mismatch at input {idx}, expected transaction {idx-latency}\");")
        else:
            lines.append("    if (out_valid !== 1'b0) $fatal(1, \"out_valid asserted before pipeline latency\");")
    for flush in range(latency):
        lines.append("    @(negedge clk); in_valid = 1'b0;")
        lines.append("    @(posedge clk); #1;")
        exp = vectors[len(vectors) - latency + flush][2]
        lines.append(f"    if (out_valid !== 1'b1 || out_data !== {_sv_signed(exp, width)}) $fatal(1, \"flush mismatch {flush}\");")
    lines.extend(["    @(negedge clk); in_valid = 0;", "    @(posedge clk); #1;",
                  "    if (out_valid !== 1'b0) $fatal(1, \"out_valid did not drain\");",
                  f"    $display(\"PASS lanes={lanes} vectors={VECTOR_COUNT} latency={latency}\");",
                  "    $finish;", "  end", "endmodule"])
    return "\n".join(lines) + "\n", latency


def run_formal(lanes: int, yosys: str, timeout: int = 180, log_dir: Path | None = None) -> dict:
    source, latency = build_sequential_miter(lanes)
    depth = 2 * latency + 4
    with tempfile.TemporaryDirectory(prefix=f"orcus-pipe-formal-{lanes}-") as tmp:
        root = Path(tmp)
        verilog, log = root / "miter.v", root / "yosys-formal.log"
        verilog.write_text(source)
        top = f"orcus_pipeline_miter_{lanes}"
        script = (f"read_verilog {verilog}; prep -top {top}; flatten; "
                  f"sat -seq {depth} -verify -prove bad 0 -set-init-zero")
        started = time.perf_counter()
        try:
            proc = subprocess.run([yosys, "-p", script], text=True, capture_output=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            if log_dir is not None:
                log_dir.mkdir(parents=True, exist_ok=True)
                (log_dir / f"{lanes}-lane-miter.v").write_text(source)
                (log_dir / "yosys-formal-timeout.log").write_text(stdout + "\\n" + stderr)
            raise TimeoutError(f"sequential SAT timeout for {lanes} lanes after {timeout}s") from exc
        elapsed = time.perf_counter() - started
        log_text = proc.stdout + "\n" + proc.stderr
        log.write_text(log_text)
        persistent_log = "yosys-formal.log"
        if log_dir is not None:
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / f"{lanes}-lane-miter.v").write_text(source)
            (log_dir / persistent_log).write_text(log_text)
        if proc.returncode:
            raise RuntimeError(f"sequential SAT failed for {lanes} lanes: {log_text[-5000:]}")
        return {"status": "PASS", "method": "Yosys SAT bounded sequential miter",
                "depth_cycles": depth, "latency_cycles": latency,
                "runtime_seconds": elapsed, "log": persistent_log}


def run_streaming(lanes: int, iverilog: str, vvp: str, timeout: int = 60, log_dir: Path | None = None) -> dict:
    source, latency = build_streaming_testbench(lanes)
    with tempfile.TemporaryDirectory(prefix=f"orcus-pipe-stream-{lanes}-") as tmp:
        root = Path(tmp)
        tb, image = root / "stream.v", root / "stream.out"
        tb.write_text(source)
        compile_run = subprocess.run([iverilog, "-g2012", "-s", "tb", "-o", str(image), str(tb)],
                                     text=True, capture_output=True, timeout=timeout)
        compile_text = compile_run.stdout + "\\n" + compile_run.stderr
        if log_dir is not None:
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / f"{lanes}-lane-stream-testbench.v").write_text(source)
            (log_dir / f"{lanes}-lane-iverilog.log").write_text(compile_text)
        if compile_run.returncode:
            raise RuntimeError(f"iverilog compile failed for {lanes} lanes: {compile_run.stderr[-4000:]}")
        try:
            sim = subprocess.run([vvp, str(image)], text=True, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            if log_dir is not None:
                (log_dir / f"{lanes}-lane-vvp-timeout.log").write_text(stdout + "\\n" + stderr)
            raise TimeoutError(f"streaming simulation timeout for {lanes} lanes after {timeout}s") from exc
        sim_text = sim.stdout + "\n" + sim.stderr
        if log_dir is not None:
            (log_dir / f"{lanes}-lane-vvp.log").write_text(sim_text)
        if sim.returncode or "PASS" not in sim.stdout:
            raise RuntimeError(f"streaming simulation failed for {lanes} lanes: {sim.stdout[-4000:]} {sim.stderr[-2000:]}")
        return {"status": "PASS", "vectors": VECTOR_COUNT, "latency_cycles": latency,
                "stdout": sim.stdout.strip(),
                "compile_log": f"{lanes}-lane-iverilog.log",
                "simulation_log": f"{lanes}-lane-vvp.log"}


def run_all(yosys: str = "yosys", iverilog: str = "iverilog", vvp: str = "vvp") -> dict:
    for binary in (yosys, iverilog, vvp):
        if not shutil.which(binary):
            raise RuntimeError(f"required validation tool not found: {binary}")
    results = []
    for lanes in LANES:
        design = generate_dadda_pipelined(lanes)
        formal = run_formal(lanes, yosys)
        streaming = run_streaming(lanes, iverilog, vvp)
        results.append({"lanes": lanes, "width": design.width,
                        "latency_cycles": design.latency,
                        "stage_targets": list(design.stage_targets),
                        "registered_heap_bits_per_stage": [
                            stage["registered_bit_count"] for stage in design.manifest["stage_boundaries"]],
                        "formal": formal, "streaming": streaming})
    return {"schema": "orcus-dadda-pipeline-validation-v1",
            "status": "complete", "seed": SEED, "vectors_per_configuration": VECTOR_COUNT,
            "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yosys", default="yosys")
    parser.add_argument("--iverilog", default="iverilog")
    parser.add_argument("--vvp", default="vvp")
    parser.add_argument("--output", type=Path, default=Path("artifacts/orcus-dadda-pipeline-validation.json"))
    args = parser.parse_args()
    report = run_all(args.yosys, args.iverilog, args.vvp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
