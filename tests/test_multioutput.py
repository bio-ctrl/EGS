import unittest

from orcus.multioutput import synthesize_multi_output
from orcus.synthesis import SynthesisConfig
from orcus.truth_table import TruthTable


class MultiOutputSynthesisTests(unittest.TestCase):
    def test_combines_outputs_and_verifies_every_truth_table(self):
        targets = {
            "ab": TruthTable.from_callable(3, lambda a, b, c: a & b),
            "ab_or_c": TruthTable.from_callable(3, lambda a, b, c: (a & b) | c),
            "ab_xor_c": TruthTable.from_callable(3, lambda a, b, c: (a & b) ^ c),
        }
        result = synthesize_multi_output(targets, SynthesisConfig(input_count=3, max_gates=5))
        self.assertTrue(result.found)
        self.assertIsNotNone(result.network)
        self.assertTrue(result.network.verify(targets))
        self.assertLessEqual(result.shared_gate_count, result.independent_gate_count)
        self.assertEqual(result.gates_saved, result.independent_gate_count - result.shared_gate_count)

    def test_rejects_mixed_input_counts(self):
        targets = {
            "two": TruthTable.constant(2, True),
            "three": TruthTable.constant(3, True),
        }
        with self.assertRaises(ValueError):
            synthesize_multi_output(targets)

    def test_reports_unreachable_output_without_partial_network(self):
        targets = {"parity": TruthTable.from_callable(3, lambda a, b, c: a ^ b ^ c)}
        result = synthesize_multi_output(targets, SynthesisConfig(input_count=3, max_gates=0))
        self.assertFalse(result.found)
        self.assertIsNone(result.network)
        self.assertEqual(result.missing_outputs, ("parity",))

    def test_requires_named_outputs(self):
        with self.assertRaises(ValueError):
            synthesize_multi_output({})


if __name__ == "__main__":
    unittest.main()
