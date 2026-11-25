import unittest

from orcus.architecture_search import (
    generate_associative_candidates,
    pareto_candidates,
    run_search,
)


class ArchitectureSearchTests(unittest.TestCase):
    def test_four_operand_add_enumerates_distinct_topologies(self):
        candidates = generate_associative_candidates("add", 4, 2)
        self.assertEqual(len(candidates), 15)
        self.assertEqual(len({candidate.topology for candidate in candidates}), 15)

    def test_every_candidate_matches_modular_reference_exhaustively(self):
        report = run_search("add", 4, 2)
        self.assertEqual(report["search_space"]["candidate_count"], 15)
        self.assertTrue(report["search_space"]["exhaustive_equivalence"])
        self.assertTrue(all(item["verification"]["passed"] for item in report["candidates"]))
        self.assertTrue(all(item["verification"]["vectors_checked"] == 256
                            for item in report["candidates"]))

    def test_operator_grammar_is_validated(self):
        with self.assertRaises(ValueError):
            generate_associative_candidates("sub", 4, 2)
        with self.assertRaises(ValueError):
            generate_associative_candidates("add", 1, 2)

    def test_candidate_cap_is_enforced(self):
        with self.assertRaises(ValueError):
            generate_associative_candidates("xor", 5, 2, max_candidates=10)

    def test_search_is_deterministic(self):
        first = generate_associative_candidates("xor", 4, 2)
        second = generate_associative_candidates("xor", 4, 2)
        self.assertEqual([item.topology for item in first],
                         [item.topology for item in second])


if __name__ == "__main__":
    unittest.main()
