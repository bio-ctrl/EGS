"""Synthesize the three canonical targets and print their circuit metrics."""

from orcus.synthesis import SynthesisConfig, SynthesisEngine
from orcus.targets import benchmark_targets
from orcus.verilog import emit_verilog


def main() -> None:
    engine = SynthesisEngine(SynthesisConfig(max_gates=7))
    for name, target in benchmark_targets().items():
        result = engine.synthesize(target)
        if not result.found or result.circuit is None:
            raise SystemExit(f"ORCUS failed to synthesize {name}")
        print(f"{name}: {result.expression}")
        print(f"  gates={result.metrics.gate_count}, depth={result.metrics.logic_depth}")
        print(emit_verilog(result.circuit))


if __name__ == "__main__":
    main()
