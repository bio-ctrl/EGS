"""ORCUS: a reproducible baseline for Boolean-architecture exploration."""

from .circuit import Circuit, CircuitMetrics, measure_circuit
from .synthesis import SynthesisConfig, SynthesisEngine, SynthesisResult
from .network import CircuitNetwork, NetworkMetrics
from .truth_table import TruthTable
from .bitvector import BitVectorGraph, DataNode, DataOutput, DataPort, DataflowMetrics, VerificationReport

__all__ = [
    "BitVectorGraph",
    "DataNode",
    "DataOutput",
    "DataPort",
    "DataflowMetrics",
    "VerificationReport",
    "Circuit",
    "CircuitMetrics",
    "CircuitNetwork",
    "SynthesisConfig",
    "SynthesisEngine",
    "SynthesisResult",
    "NetworkMetrics",
    "TruthTable",
    "measure_circuit",
]

__version__ = "0.1.0"
