import unittest
from orcus.compressor import build_compressor_network, verify_exhaustive


class CompressorNetworkTests(unittest.TestCase):
    def test_all_schedules_exhaustive_small(self):
        for schedule in ("wallace", "wallace_reverse", "dadda"):
            for operands, width in ((3, 2), (4, 2), (5, 2)):
                network = build_compressor_network(operands, width, schedule)
                report = verify_exhaustive(network, max_input_bits=12)
                self.assertTrue(report["passed"], (schedule, operands, width, report))
                self.assertTrue(report["exhaustive"])

    def test_random_width_values(self):
        for schedule in ("wallace", "wallace_reverse", "dadda"):
            network = build_compressor_network(6, 8, schedule)
            for values in ((0, 0, 0, 0, 0, 0), (255,)*6, (1, 2, 3, 4, 5, 6),
                           (127, 128, 129, 130, 131, 132)):
                self.assertEqual(network.evaluate(values), sum(values))

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            build_compressor_network(2, 8)
        with self.assertRaises(ValueError):
            build_compressor_network(3, 0)


if __name__ == "__main__":
    unittest.main()
