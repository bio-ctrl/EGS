import unittest

from orcus.adder_search import (
    dominates,
    generate_adder_candidates,
    pareto_frontier,
    search_report,
)


class AdderSearchTests(unittest.TestCase):
    def test_generates_three_distinct_architectures(self):
        candidates = generate_adder_candidates(8)
        self.assertEqual({item.name for item in candidates},
                         {"ripple", "sklansky", "kogge_stone"})

    def test_every_candidate_is_exhaustively_verified(self):
        report = search_report(4)
        self.assertEqual(report["search"]["candidate_count"], 3)
        for candidate in report["candidates"]:
            self.assertTrue(candidate["verification"]["passed"])
            self.assertTrue(candidate["verification"]["exhaustive"])
            self.assertEqual(candidate["verification"]["vectors_checked"], 256)

    def test_pareto_dominance(self):
        self.assertTrue(dominates((4, 5, 2), (5, 5, 3)))
        self.assertFalse(dominates((4, 5, 2), (4, 5, 2)))
        self.assertFalse(dominates((6, 2, 3), (5, 4, 2)))

    def test_frontier_retains_tradeoffs(self):
        candidates = generate_adder_candidates(16)
        frontier = pareto_frontier(candidates)
        self.assertGreaterEqual(len(frontier), 1)
        self.assertTrue(all(item in candidates for item in frontier))


if __name__ == "__main__":
    unittest.main()
