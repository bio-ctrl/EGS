import unittest
from orcus.compressor import build_compressor_network, verify_exhaustive

class CompressorNetworkTests(unittest.TestCase):
    def test_all_schedules_exhaustive_small(self):
        for schedule in ("wallace", "wallace_reverse", "dadda"):
            for final_adder in ("ripple", "kogge_stone", "sklansky"):
                for operands, width in ((3, 2), (4, 2), (5, 2)):
                    network = build_compressor_network(operands, width, schedule, final_adder)
                    report = verify_exhaustive(network, max_input_bits=12)
                    self.assertTrue(report["passed"], (schedule, final_adder, operands, width, report))
                    self.assertTrue(report["exhaustive"])

    def test_random_width_values(self):
        for schedule in ("wallace", "wallace_reverse", "dadda"):
            for final_adder in ("ripple", "kogge_stone", "sklansky"):
                network = build_compressor_network(6, 8, schedule, final_adder)
                for values in ((0, 0, 0, 0, 0, 0), (255,)*6, (1, 2, 3, 4, 5, 6),
                               (127, 128, 129, 130, 131, 132)):
                    self.assertEqual(network.evaluate(values), sum(values))

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            build_compressor_network(2, 8)
        with self.assertRaises(ValueError):
            build_compressor_network(3, 0)

    def test_exhaustive_budget_is_reported_as_skipped(self):
        network = build_compressor_network(4, 8)
        report = verify_exhaustive(network, max_input_bits=16)
        self.assertIsNone(report["passed"])
        self.assertFalse(report["exhaustive"])
        self.assertEqual(report["vectors_checked"], 0)
        self.assertEqual(report["reason"], "input-bit budget exceeded")

    def test_invalid_exhaustive_budget(self):
        network = build_compressor_network(3, 2)
        for budget in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                verify_exhaustive(network, max_input_bits=budget)

    def test_verilog_module_name_validation(self):
        network = build_compressor_network(3, 2)
        for name in ("", "1invalid", "bad-name", "has space"):
            with self.assertRaises(ValueError):
                network.emit_verilog(name)
        self.assertIn("module valid_name(", network.emit_verilog("valid_name"))

if __name__ == "__main__":
    unittest.main()
