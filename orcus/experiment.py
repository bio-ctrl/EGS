"""Reproducible experiment harness and machine-readable result records."""

from __future__ import annotations

import json
import platform
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .synthesis import SynthesisConfig, SynthesisEngine
from .targets import benchmark_targets


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    experiment_id: str
    timestamp_utc: str
    python_version: str
    platform: str
    target_name: str
    target_truth_table: str
    max_gates: int
    allowed_gates: tuple[str, ...]
    found: bool
    gate_count: int | None
    logic_depth: int | None
    max_fanout: int | None
    elapsed_seconds: float
    explored_functions: int
    verified: bool


def run_standard_suite(max_gates: int = 7) -> list[dict]:
    records: list[dict] = []
    targets = benchmark_targets()
    for name, target in targets.items():
        config = SynthesisConfig(max_gates=max_gates, input_count=target.input_count)
        engine = SynthesisEngine(config)
        result = engine.synthesize(target)
        metrics = result.metrics
        records.append(asdict(ExperimentRecord(
            experiment_id=f"orcus-baseline-{name}-v0.1.0",
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            target_name=name,
            target_truth_table=target.hex(),
            max_gates=max_gates,
            allowed_gates=config.gates,
            found=result.found,
            gate_count=None if metrics is None else metrics.gate_count,
            logic_depth=None if metrics is None else metrics.logic_depth,
            max_fanout=None if metrics is None else metrics.max_fanout,
            elapsed_seconds=result.elapsed_seconds,
            explored_functions=result.explored_functions,
            verified=result.found and result.circuit is not None and result.circuit.verify(target),
        )))
    return records


def write_jsonl(records: Iterable[dict], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
