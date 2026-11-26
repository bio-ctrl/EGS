import unittest
from benchmarks.signed_int4_dot_product import VARIANTS, module_source


class SignedInt4DotProductTests(unittest.TestCase):
    def test_all_variants_share_identical_multiplier_and_extension_lines(self):
        common = []
        for variant in VARIANTS:
            source = module_source("dut", variant)
            lines = [line.strip() for line in source.splitlines()
                     if "wire signed [7:0] p" in line or "wire signed [9:0] e" in line]
            if not common:
                common = lines
            else:
                self.assertEqual(lines, common)

    def test_all_variants_use_ten_bit_signed_accumulator(self):
        for variant in VARIANTS:
            source = module_source("dut", variant)
            self.assertIn("output signed [9:0] y", source)

    def test_carry_save_reduction_is_present(self):
        source = module_source("dut", "carry_save")
        self.assertIn("wire [9:0] s0", source)
        self.assertIn("wire [9:0] c1", source)
        self.assertIn("assign y = s1 + c1;", source)


if __name__ == "__main__":
    unittest.main()
