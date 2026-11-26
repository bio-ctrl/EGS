import unittest
from benchmarks.signed_int4_dot_product import VARIANTS, module_source


class SignedInt4DotProductTests(unittest.TestCase):
    def test_product_level_baselines_share_identical_multiplier_lines(self):
        common = None
        for variant in VARIANTS:
            if variant == "fused_partial_product":
                continue
            source = module_source("dut", variant)
            lines = [line.strip() for line in source.splitlines()
                     if "wire signed [7:0] p" in line or "wire signed [9:0] e" in line]
            if common is None:
                common = lines
            else:
                self.assertEqual(lines, common)

    def test_fused_candidate_uses_shared_partial_product_heap(self):
        source = module_source("dut", "fused_partial_product")
        self.assertIn("wire pp_0_0_0", source)
        self.assertIn("wire pp_3_3_3", source)
        self.assertIn("wire fa_s_", source)
        self.assertIn("wire fa_c_", source)
        self.assertIn("assign y = fused_row0 + fused_row1;", source)
        self.assertNotIn("wire signed [7:0] p0", source)

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
