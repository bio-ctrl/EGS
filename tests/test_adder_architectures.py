import unittest

from orcus.adder_architectures import (
    build_kogge_stone_adder,
    build_ripple_carry_adder,
)


class AdderArchitectureTests(unittest.TestCase):
    def test_both_architectures_are_exhaustively_equivalent(self):
        for width in range(1, 5):
            limit = 1 << width
            expected = build_ripple_carry_adder(width)
            candidate = build_kogge_stone_adder(width)
            for a in range(limit):
                for b in range(limit):
                    self.assertEqual(expected.evaluate(a, b), a + b)
                    self.assertEqual(candidate.evaluate(a, b), a + b)

    def test_prefix_depth_is_lower_for_sixteen_bits(self):
        ripple = build_ripple_carry_adder(16).metrics()
        prefix = build_kogge_stone_adder(16).metrics()
        self.assertLess(prefix.logic_depth, ripple.logic_depth)

    def test_verilog_emission_is_synthesizable_source(self):
        source = build_kogge_stone_adder(4).emit_verilog()
        self.assertIn("module orcus_kogge_stone_4", source)
        self.assertIn("assign sum[4]", source)
        self.assertTrue(source.rstrip().endswith("endmodule"))

    def test_rejects_invalid_width_and_inputs(self):
        with self.assertRaises(ValueError):
            build_ripple_carry_adder(0)
        with self.assertRaises(ValueError):
            build_kogge_stone_adder(65)
        with self.assertRaises(ValueError):
            build_ripple_carry_adder(3).evaluate(8, 0)


if __name__ == "__main__":
    unittest.main()
