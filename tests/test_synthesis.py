import unittest

from orcus.synthesis import SynthesisConfig, SynthesisEngine
from orcus.targets import benchmark_targets
from orcus.truth_table import TruthTable


class SynthesisTests(unittest.TestCase):
    def test_standard_targets_are_found_and_exhaustively_verified(self):
        engine = SynthesisEngine(SynthesisConfig(max_gates=7))
        for name, target in benchmark_targets().items():
            with self.subTest(target=name):
                result = engine.synthesize(target)
                self.assertTrue(result.found)
                self.assertIsNotNone(result.circuit)
                self.assertTrue(result.circuit.verify(target))
                self.assertEqual(result.metrics.gate_count, result.search_depth)

    def test_truth_table_identity_is_minimal_zero_gate(self):
        target = TruthTable.variable(3, 1)
        result = SynthesisEngine(SynthesisConfig(max_gates=4)).synthesize(target)
        self.assertTrue(result.found)
        self.assertEqual(result.metrics.gate_count, 0)
        self.assertEqual(result.metrics.logic_depth, 0)

    def test_max_gate_limit_can_report_not_found(self):
        target = benchmark_targets()["parity3"]
        result = SynthesisEngine(SynthesisConfig(max_gates=0)).synthesize(target)
        self.assertFalse(result.found)
        self.assertIsNone(result.circuit)

    def test_all_256_three_input_functions_are_reached_and_verified(self):
        from orcus.circuit import Circuit

        engine = SynthesisEngine(SynthesisConfig(max_gates=4))
        catalogue = engine.enumerate()
        self.assertEqual(len(catalogue), 256)
        for truth_bits, expr in catalogue.items():
            with self.subTest(truth_table=truth_bits):
                target = TruthTable(3, truth_bits)
                circuit = Circuit.from_expression(expr, 3)
                self.assertTrue(circuit.verify(target))
                self.assertLessEqual(expr.gate_count, 4)

    def test_target_input_count_must_match(self):
        engine = SynthesisEngine(SynthesisConfig(input_count=3))
        with self.assertRaises(ValueError):
            engine.synthesize(TruthTable.constant(2, True))

    def test_enumerator_caches_work(self):
        engine = SynthesisEngine(SynthesisConfig(max_gates=5))
        first = engine.enumerate(3)
        count = len(first)
        second = engine.enumerate(3)
        self.assertEqual(len(second), count)
        self.assertEqual(engine._enumerated_to, 3)


if __name__ == "__main__":
    unittest.main()
