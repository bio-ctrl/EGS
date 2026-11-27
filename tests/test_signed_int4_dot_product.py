import shutil
import unittest

from benchmarks.signed_int4_dot_product import (
    VARIANTS,
    _parse_opensta_power_report,
    module_source,
)
from orcus.typed_heap import (
    audit_fused_heap, generate_fused_heap, run_compositional_proofs,
    tampered_manifest_carry_weight,
)


FORMAL_TEST_TIMEOUT_SECONDS = 120


class SignedInt4DotProductTests(unittest.TestCase):

    def test_compositional_sat_proofs_and_heap_audit(self):
        yosys = shutil.which("yosys")
        if not yosys:
            self.skipTest("Yosys is required for compositional SAT proof")
        candidate = module_source("orcus_fused_partial_product", "fused_partial_product")
        result = run_compositional_proofs(candidate, yosys)
        self.assertEqual(result["formal_equivalence"], "formal-pass")
        self.assertEqual(len(result["proof_lemmas"]), 4)
        self.assertEqual(result["heap_audit"]["status"], "pass")
        self.assertIn("half_adder", [n["kind"] for n in result["heap_manifest"]["compressors"]])

    def test_negative_tamper_partial_product_polarity(self):
        lines, manifest = generate_fused_heap(4)
        changed = list(lines)
        target = "  wire pp_0_3_0 = ~(a0[3] & b0[0]);"
        self.assertIn(target, changed)
        changed[changed.index(target)] = "  wire pp_0_3_0 = (a0[3] & b0[0]);"
        with self.assertRaisesRegex(ValueError, "polarity/source mismatch"):
            audit_fused_heap(changed, manifest)

    def test_negative_tamper_compressor_carry_weight(self):
        lines, manifest = generate_fused_heap(4)
        tampered = tampered_manifest_carry_weight(manifest)
        with self.assertRaisesRegex(ValueError, "carry weight"):
            audit_fused_heap(lines, tampered)

    def test_negative_tamper_output_bit(self):
        lines, manifest = generate_fused_heap(4)
        changed = list(lines)
        target = "  assign y = fused_row0 + fused_row1;"
        self.assertIn(target, changed)
        changed[changed.index(target)] = "  assign y = (fused_row0 + fused_row1) ^ 10'b0000000001;"
        with self.assertRaisesRegex(ValueError, "final 10-bit CPA output"):
            audit_fused_heap(changed, manifest)

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

    def test_opensta_parser_preserves_all_power_components_and_vcd_annotation(self):
        report = """Annotated 259 pin activities.
Group                    Internal    Switching      Leakage        Total
                            Power        Power        Power        Power (Watts)
------------------------------------------------------------------------
Total                4.788638e-05 4.371745e-05 1.341678e-05 1.050206e-04 100.0%
"""
        parsed = _parse_opensta_power_report(report)
        self.assertAlmostEqual(parsed["power_internal_uw"], 47.88638, places=5)
        self.assertAlmostEqual(parsed["power_switching_uw"], 43.71745, places=5)
        self.assertAlmostEqual(parsed["power_leakage_uw"], 13.41678, places=5)
        self.assertAlmostEqual(parsed["power_total_uw"], 105.0206, places=4)
        self.assertEqual(parsed["annotated_pin_activities"], 259)

    def test_opensta_parser_rejects_missing_vcd_annotation(self):
        report = """Group Internal Switching Leakage Total
Power Power Power Power (Watts)
Total 1e-6 2e-6 3e-6 6e-6 100.0%
"""
        with self.assertRaisesRegex(RuntimeError, "VCD pin activity annotation"):
            _parse_opensta_power_report(report)

    def test_carry_save_reduction_is_present(self):
        source = module_source("dut", "carry_save")
        self.assertIn("wire [9:0] s0", source)
        self.assertIn("wire [9:0] c1", source)
        self.assertIn("assign y = s1 + c1;", source)


if __name__ == "__main__":
    unittest.main()
