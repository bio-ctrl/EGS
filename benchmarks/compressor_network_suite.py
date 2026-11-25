"""Reproducible compressor-network experiment with Yosys SAT and synth/stat."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from orcus.compressor import build_compressor_network, verify_exhaustive


def run_yosys(network, require=False):
    yosys = shutil.which("yosys")
    if not yosys:
        if require:
            raise RuntimeError("Yosys is required but was not found")
        return {"available": False}
    pad = network.output_width - network.width
    terms = []
    for i in range(network.operand_count):
        terms.append(f"x{i}" if pad == 0 else "{{" + f"{pad}{{1'b0}}" + "}, " + f"x{i}" + "}")
    ref = " + ".join(terms)
    reference = (f"module reference({', '.join([f'input [{network.width-1}:0] x{i}' for i in range(network.operand_count)])}, "
                 f"output [{network.output_width-1}:0] sum); assign sum = {ref}; endmodule\n")
    candidate = network.emit_verilog("candidate")
    with tempfile.TemporaryDirectory() as tmp:
        cand_path, ref_path = Path(tmp)/"candidate.v", Path(tmp)/"reference.v"
        cand_path.write_text(candidate)
        ref_path.write_text(reference)
        proof_script = (f"read_verilog {cand_path} {ref_path}; "
                        "proc; flatten candidate; "
                        "miter -equiv -flatten reference candidate m; "
                        "sat -verify -prove trigger 0 m")
        proof = subprocess.run([yosys, "-p", proof_script], text=True, capture_output=True)
        if proof.returncode:
            raise RuntimeError(proof.stdout + "\n" + proof.stderr)
        formal_passed = "SAT proof finished - no model found: SUCCESS!" in proof.stdout
        if not formal_passed:
            raise RuntimeError("Yosys completed without the expected successful SAT proof marker")
        def synth_count(path, top):
            script = f"read_verilog {path}; hierarchy -top {top}; synth -top {top}; stat"
            result = subprocess.run([yosys, "-p", script], text=True, capture_output=True)
            if result.returncode:
                raise RuntimeError(result.stdout + "\n" + result.stderr)
            counts = [line.split(":")[-1].strip() for line in result.stdout.splitlines()
                      if "Number of cells:" in line]
            return int(counts[-1]) if counts else None
        candidate_cells = synth_count(cand_path, "candidate")
        reference_cells = synth_count(ref_path, "reference")
        return {"available": True, "version": subprocess.run(
            [yosys, "-V"], text=True, capture_output=True).stdout.strip(),
            "formal_passed": formal_passed,
            "candidate_generic_cells": candidate_cells,
            "reference_generic_cells": reference_cells,
            "cell_count_delta_candidate_minus_reference": (
                candidate_cells - reference_cells
                if candidate_cells is not None and reference_cells is not None else None),
            "proof_log_tail": proof.stdout[-1200:]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--operands", type=int, default=4)
    parser.add_argument("--width", type=int, default=3)
    parser.add_argument("--require-yosys", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = []
    for schedule in ("wallace", "wallace_reverse", "dadda"):
        network = build_compressor_network(args.operands, args.width, schedule)
        verification = verify_exhaustive(network, max_input_bits=16)
        synthesis = run_yosys(network, args.require_yosys)
        results.append({"schedule": schedule, "metrics": network.metrics(),
                        "verification": verification, "yosys": synthesis,
                        "verilog": network.emit_verilog()})
    report = {"experiment": "multi_operand_compressor_networks",
              "operands": args.operands, "width": args.width,
              "output_width": args.width + (args.operands-1).bit_length(),
              "results": results,
              "limitations": ["bounded schedule family", "generic synthesis is not physical PPA",
                              "Wallace and Dadda are established reference architectures",
                              "no novelty or commercial-performance claim"]}
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n")
    print(payload)


if __name__ == "__main__":
    main()
