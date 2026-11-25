import unittest

from orcus.joint_search import JointSearchConfig, search_multi_output_joint
from orcus.synthesis import SynthesisConfig
from orcus.truth_table import TruthTable


class JointMultiOutputSearchTests(unittest.TestCase):
    def test_retains_alternative_implementations_and_verifies_joint_network(self):
        targets = {
            "ab": TruthTable.from_callable(3, lambda a, b, c: a & b),
            "ab_or_c": TruthTable.from_callable(3, lambda a, b, c: (a & b) | c),
        }
        config = JointSearchConfig(
            synthesis=SynthesisConfig(input_count=3, max_gates=3),
            candidates_per_truth_per_cost=4,
            max_generated_expressions=100_000,
            max_combinations=10_000,
        )
        result = search_multi_output_joint(targets, config)
        self.assertTrue(result.found)
        self.assertTrue(result.network.verify(targets))
        self.assertGreaterEqual(dict(result.candidates_per_output)["ab"], 2)
        self.assertGreater(result.combinations_evaluated, 1)
        self.assertIsNotNone(result.joint_gate_count)

    def test_reports_combination_limit_without_claiming_global_optimum(self):
        targets = {
            "ab": TruthTable.from_callable(3, lambda a, b, c: a & b),
            "ab_or_c": TruthTable.from_callable(3, lambda a, b, c: (a & b) | c),
        }
        config = JointSearchConfig(
            synthesis=SynthesisConfig(input_count=3, max_gates=2),
            max_combinations=1,
        )
        result = search_multi_output_joint(targets, config)
        self.assertTrue(result.found)
        self.assertEqual(result.combinations_evaluated, 1)
        self.assertTrue(result.search_truncated)
        self.assertTrue(result.network.verify(targets))

    def test_rejects_mixed_input_counts(self):
        with self.assertRaises(ValueError):
            search_multi_output_joint({
                "two": TruthTable.constant(2, True),
                "three": TruthTable.constant(3, True),
            })

    def test_rejects_non_truth_table_target(self):
        with self.assertRaises(TypeError):
            search_multi_output_joint({"bad": "not a truth table"})


if __name__ == "__main__":
    unittest.main()
