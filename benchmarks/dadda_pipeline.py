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


def _weighted_sum(heap: list[list[str]], width: int, prefix: str) -> tuple[list[str], str]:
    terms = []
    declarations = []
    for column, tokens in enumerate(heap):
        for index, token in enumerate(tokens):
            term = f"{prefix}_term_{column}_{index}"
            declarations.append(
                f"  wire [{width - 1}:0] {term} = "
                f"{{{{{width - 1}{{1'b0}}}}, {token}}} << {column};"
            )
            terms.append(term)
    expression = " + ".join(terms) if terms else f"{width}'b0"
    return declarations, expression


def build_initial_heap_miter(lanes: int, lane_index: int = 0) -> str:
    """Prove one lane's Baugh-Wooley heap equals its signed 4x4 product."""
    if lane_index < 0 or lane_index >= lanes:
        raise ValueError(f"invalid lane {lane_index} for {lanes} lanes")
    design = generate_dadda_pipelined(lanes)
    width = design.width
    all_heap = design.manifest["stage_boundaries"][0]["input_heap"]
    prefix = f"_{lane_index}_"
    lane_heap = [
        [token for token in column if token.startswith(("pp" + prefix, "bias" + prefix))]
        for column in all_heap
    ]
    ports = [
        f"input wire signed [3:0] a{lane_index}",
        f"input wire signed [3:0] b{lane_index}",
        "output wire bad",
    ]
    lines = [f"module orcus_dadda_initial_heap_miter_{lanes}_{lane_index}({', '.join(ports)});"]

    for i in range(4):
        for j in range(4):
            name = f"pp_{lane_index}_{i}_{j}"
            product = f"(a{lane_index}[{i}] & b{lane_index}[{j}])"
            inverted = (i == 3) != (j == 3)
            lines.append(f"  wire {name} = " + (f"~{product};" if inverted else f"{product};"))
    lane_tokens = {token for column in lane_heap for token in column}
    for bit in range(width):
        bias = f"bias_{lane_index}_{bit}"
        if bias in lane_tokens:
            lines.append(f"  wire {bias} = 1'b1;")

    lines.append(
        f"  wire signed [7:0] signed_a = {{{{4{{a{lane_index}[3]}}}}, a{lane_index}}};"
    )
    lines.append(
        f"  wire signed [7:0] signed_b = {{{{4{{b{lane_index}[3]}}}}, b{lane_index}}};"
    )
    lines.append("  wire signed [7:0] signed_product = signed_a * signed_b;")
    lines.append(
        f"  wire signed [{width - 1}:0] extended_product = "
        f"{{{{{width - 8}{{signed_product[7]}}}}, signed_product}};"
    )
    heap_decls, heap_expr = _weighted_sum(lane_heap, width, "initial")
    lines.extend(heap_decls)
    lines.append(f"  wire [{width - 1}:0] initial_heap_sum = {heap_expr};")
    lines.append("  assign bad = (initial_heap_sum != extended_product);")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"



def build_stage_miter(lanes: int, stage_index: int) -> str:
    """Build a standalone combinational weighted-heap equivalence miter.

    Inputs are arbitrary heap bits. Compressor equations are reconstructed
    from the generator manifest, so each stage is proved independently of
    all earlier pipeline logic and register boundaries.
    """
    design = generate_dadda_pipelined(lanes)
    boundaries = design.manifest["stage_boundaries"]
    if stage_index < 0 or stage_index >= len(boundaries):
        raise ValueError(f"invalid stage {stage_index} for {lanes} lanes")
    boundary = boundaries[stage_index]
    input_heap = boundary["input_heap"]
    output_heap = boundary["output_heap"]
    input_tokens = list(dict.fromkeys(token for col in input_heap for token in col))
    declarations = [f"input wire {token}" for token in input_tokens]
    lines = [
        f"module orcus_dadda_stage_miter_{lanes}_{stage_index}(",
        ", ".join(declarations + ["output wire bad"]),
        ");",
    ]
    compressor_records = [
        record for record in design.manifest["compressors"]
        if record["stage"] == stage_index
    ]
    for record in compressor_records:
        x = record["inputs"][0]
        y = record["inputs"][1]
        if record["kind"] == "full_adder":
            z = record["inputs"][2]
            lines.append(f"  wire {record['sum']} = {x} ^ {y} ^ {z};")
            if record["carry"] is not None:
                lines.append(
                    f"  wire {record['carry']} = ({x} & {y}) | ({x} & {z}) | ({y} & {z});"
                )
        else:
            lines.append(f"  wire {record['sum']} = {x} ^ {y};")
            if record["carry"] is not None:
                lines.append(f"  wire {record['carry']} = {x} & {y};")

    in_decls, in_expr = _weighted_sum(input_heap, design.width, "in")
    out_decls, out_expr = _weighted_sum(output_heap, design.width, "out")
    lines.extend(in_decls)
    lines.extend(out_decls)
    lines.append(f"  wire [{design.width - 1}:0] weighted_input = {in_expr};")
    lines.append(f"  wire [{design.width - 1}:0] weighted_output = {out_expr};")
    if stage_index == design.latency - 1:
        row0 = [column[0] if column else "1'b0" for column in output_heap]
        row1 = [column[1] if len(column) > 1 else "1'b0" for column in output_heap]
        row0_expr = "{"+", ".join(reversed(row0))+"}"
        row1_expr = "{"+", ".join(reversed(row1))+"}"
        lines.append(f"  wire [{design.width - 1}:0] final_row0 = {row0_expr};")
        lines.append(f"  wire [{design.width - 1}:0] final_row1 = {row1_expr};")
        lines.append(
            f"  wire [{design.width - 1}:0] final_cpa = final_row0 + final_row1;"
        )
        lines.append(
            "  assign bad = (weighted_input != weighted_output) || "
            "(final_cpa != weighted_output);"
        )
    else:
        lines.append("  assign bad = (weighted_input != weighted_output);")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def build_control_miter(lanes: int) -> tuple[str, int]:
    """Compare post-edge DUT valid against a reference including out_valid.

    The DUT contains LATENCY reduction-stage valid registers plus the
    separately registered out_valid boundary.  The reference therefore needs
    LATENCY + 1 bits for a post-edge comparison, while transaction latency
    remains LATENCY rising-edge intervals from input sampling to output.
    """
    design = generate_dadda_pipelined(lanes)
    latency = design.latency
    reference_depth = latency + 1
    ports = ["input wire clk", "input wire reset", "input wire in_valid", "output wire bad"]
    lines = [f"module orcus_pipeline_control_miter_{lanes}({', '.join(ports)});",
             "  wire dut_valid;",
             f"  wire signed [{design.width - 1}:0] dut_data;"]
    dut_ports = [".clk(clk)", ".reset(reset)", ".in_valid(in_valid)",
                 ".out_valid(dut_valid)", ".out_data(dut_data)"]
    for lane in range(lanes):
        lines.append(f"  wire signed [3:0] a{lane} = 4'sd0;")
        lines.append(f"  wire signed [3:0] b{lane} = 4'sd0;")
        dut_ports.extend((f".a{lane}(a{lane})", f".b{lane}(b{lane})"))
    lines.append(f"  orcus_dadda_pipelined_{lanes} dut ({', '.join(dut_ports)});")
    lines.append(f"  reg [{reference_depth - 1}:0] ref_valid_pipe;")
    lines.append("  always @(posedge clk) begin")
    lines.append("    if (reset) ref_valid_pipe <= 0;")
    lines.append("    else begin")
    lines.append("      ref_valid_pipe[0] <= in_valid;")
    for index in range(1, reference_depth):
        lines.append(f"      ref_valid_pipe[{index}] <= ref_valid_pipe[{index - 1}];")
    lines.extend(["    end", "  end"])
    lines.append(f"  assign bad = (dut_valid != ref_valid_pipe[{reference_depth - 1}]);")
    lines.append("endmodule")
    return design.source + "\n" + "\n".join(lines) + "\n", latency


def build_sequential_miter(lanes: int) -> tuple[str, int]:
    """Compatibility alias: return the control-only sequential miter."""
    return build_control_miter(lanes)

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
                  "    @(negedge clk); in_valid = 1'b1;"])
    for lane in range(lanes):
        lines.append(f"    a{lane} = 4'sd0; b{lane} = 4'sd0;")
    lines.extend(["    @(posedge clk); #1;",
                  "    @(negedge clk); reset = 1'b1; in_valid = 1'b0;",
                  "    @(posedge clk); #1;",
                  "    if (out_valid !== 1'b0) $fatal(1, \"reset failed to clear valid\");",
                  "    @(negedge clk); reset = 1'b0;"])
    for _ in range(latency + 1):
        lines.extend(["    @(posedge clk); #1;",
                      "    if (out_valid !== 1'b0) $fatal(1, \"stale transaction leaked after reset\");"])
    lines.extend([f"    $display(\"PASS lanes={lanes} vectors={VECTOR_COUNT} latency={latency}\");",
                  "    $finish;", "  end", "endmodule"])
    return "\n".join(lines) + "\n", latency


def run_formal(lanes: int, yosys: str, timeout: int = 180, log_dir: Path | None = None) -> dict:
    """Prove each compressor stage independently, then prove valid/reset control.

    No sequential multiplier datapath is unrolled. The only sequential SAT
    instance observes the DUT's valid output and is optimized to its control
    cone before SAT.
    """
    if not shutil.which(yosys):
        raise RuntimeError(f"required validation tool not found: {yosys}")
    design = generate_dadda_pipelined(lanes)
    results = []
    with tempfile.TemporaryDirectory(prefix=f"orcus-pipe-compositional-{lanes}-") as tmp:
        root = Path(tmp)

        def execute(label: str, source: str, top: str, sequential: bool) -> dict:
            verilog = root / f"{label}.v"
            log = root / f"{label}.log"
            verilog.write_text(source)
            prep = f"read_verilog {verilog}; prep -top {top}; flatten; opt_clean -purge;"
            if sequential:
                depth = 2 * design.latency + 2
                sat = (f"sat -seq {depth} -tempinduct -verify -prove bad 0 "
                       "-set-init-zero")
            else:
                depth = None
                sat = "sat -verify -prove bad 0"
            started = time.perf_counter()
            try:
                proc = subprocess.run([yosys, "-p", prep + " " + sat],
                                      text=True, capture_output=True, timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                log_text = stdout + "\n" + stderr
                if log_dir is not None:
                    log_dir.mkdir(parents=True, exist_ok=True)
                    (log_dir / f"{label}.v").write_text(source)
                    (log_dir / f"{label}-timeout.log").write_text(log_text)
                raise TimeoutError(f"{label} formal timeout for {lanes} lanes after {timeout}s") from exc
            elapsed = time.perf_counter() - started
            log_text = proc.stdout + "\n" + proc.stderr
            log.write_text(log_text)
            if log_dir is not None:
                log_dir.mkdir(parents=True, exist_ok=True)
                (log_dir / f"{label}.v").write_text(source)
                (log_dir / f"{label}.log").write_text(log_text)
            if proc.returncode:
                raise RuntimeError(
                    f"{label} formal failed for {lanes} lanes: {log_text[-5000:]}"
                )
            result = {"status": "PASS", "runtime_seconds": elapsed, "log": f"{label}.log"}
            if depth is not None:
                result["depth_cycles"] = depth
                result["method"] = "Yosys sequential temporal induction on valid/reset control cone"
            else:
                result["method"] = "Yosys combinational SAT weighted-heap equivalence"
            return result

        initial_proofs = []
        for lane_index in range(lanes):
            initial_source = build_initial_heap_miter(lanes, lane_index)
            initial_top = f"orcus_dadda_initial_heap_miter_{lanes}_{lane_index}"
            proof = execute(f"initial-baugh-wooley-lane-{lane_index}",
                            initial_source, initial_top, sequential=False)
            proof["lane"] = lane_index
            initial_proofs.append(proof)

        for stage_index in range(design.latency):
            stage_source = build_stage_miter(lanes, stage_index)
            stage_top = f"orcus_dadda_stage_miter_{lanes}_{stage_index}"
            result = execute(f"stage-{stage_index}-heap-equivalence",
                             stage_source, stage_top, sequential=False)
            result["stage"] = stage_index
            result["target_height"] = design.stage_targets[stage_index]
            result["final_cpa_included"] = stage_index == design.latency - 1
            results.append(result)

        control_source, latency = build_control_miter(lanes)
        control_top = f"orcus_pipeline_control_miter_{lanes}"
        control = execute("control-valid-reset-induction",
                          control_source, control_top, sequential=True)

    return {
        "status": "PASS",
        "method": "compositional stage SAT plus sequential control induction",
        "latency_cycles": latency,
        "initial_heap_proofs": initial_proofs,
        "stage_proofs": results,
        "control_proof": control,
    }

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
