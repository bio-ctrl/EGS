import unittest

from orcus.architecture_search import (
    CANONICALIZER_VERSION,
    generate_associative_candidates,
    pareto_candidates,
    run_search,
)


class ArchitectureSearchTests(unittest.TestCase):
    def test_four_operand_add_enumerates_distinct_topologies(self):
        candidates = generate_associative_candidates("add", 4, 2)
        self.assertEqual(len(candidates), 15)
        self.assertEqual(len({candidate.digest for candidate in candidates}), 15)

    def test_every_candidate_matches_modular_reference_exhaustively(self):
        report = run_search("add", 4, 2)
        self.assertEqual(report["search_space"]["candidate_count"], 15)
        self.assertTrue(report["search_space"]["exhaustive_equivalence"])
        self.assertTrue(all(item["verification"]["passed"] for item in report["candidates"]))
        self.assertTrue(all(item["verification"]["vectors_checked"] == 256
                            for item in report["candidates"]))
        self.assertIn("wins", report["outcomes"])
        self.assertIn("ties", report["outcomes"])
        self.assertIn("regressions", report["outcomes"])
        self.assertGreaterEqual(report["runtime"]["elapsed_seconds"], 0)

    def test_operator_grammar_is_validated(self):
        with self.assertRaises(ValueError):
            generate_associative_candidates("sub", 4, 2)
        with self.assertRaises(ValueError):
            generate_associative_candidates("add", 1, 2)

    def test_candidate_cap_returns_partial_results_without_crashing(self):
        report = run_search("xor", 5, 2, max_candidates=10)
        self.assertEqual(report["search_space"]["candidate_count"], 10)
        self.assertTrue(report["search_space"]["candidate_budget_exhausted"])
        self.assertEqual(report["search_space"]["stop_reason"], "candidate-budget-exhausted")
        self.assertEqual(len(report["candidates"]), 10)

    def test_wider_search_marks_verification_as_not_run(self):
        report = run_search("add", 5, 4)
        self.assertFalse(report["search_space"]["exhaustive_equivalence"])
        self.assertTrue(all(item["verification"]["status"] == "not-run"
                            for item in report["candidates"]))

    def test_search_is_deterministic(self):
        first = generate_associative_candidates("xor", 4, 2)
        second = generate_associative_candidates("xor", 4, 2)
        self.assertEqual([item.digest for item in first], [item.digest for item in second])
        self.assertEqual(CANONICALIZER_VERSION, "ac-tree-v1")

    def test_candidate_identity_changes_with_width(self):
        narrow = generate_associative_candidates("add", 4, 2)
        wide = generate_associative_candidates("add", 4, 3)
        self.assertNotEqual([x.digest for x in narrow], [x.digest for x in wide])


if __name__ == "__main__":
    unittest.main()
