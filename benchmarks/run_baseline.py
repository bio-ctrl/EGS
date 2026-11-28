"""Run the standard ORCUS baseline suite from a source checkout."""

from pathlib import Path

from orcus.experiment import run_standard_suite, write_jsonl


if __name__ == "__main__":
    output = Path("artifacts/baseline.jsonl")
    records = run_standard_suite(max_gates=7)
    write_jsonl(records, output)
    for row in records:
        print(
            f"{row['target_name']:10s} found={row['found']} gates={row['gate_count']} "
            f"depth={row['logic_depth']} explored={row['explored_functions']} "
            f"elapsed={row['elapsed_seconds']:.6f}s verified={row['verified']}"
        )
    print(f"Wrote {output}")
