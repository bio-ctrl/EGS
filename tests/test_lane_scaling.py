import shutil
import unittest

from orcus.lane_scaling import (
    TARGET_LANES, accumulator_width, audit_fused_heap, baugh_wooley_bias,
    generate_fused_heap, module_source, run_compositional_proofs,
    run_yosys_equivalence, tamper_compressor_carry_weight,
    tamper_output_bit, tamper_partial_product_polarity,
)
from benchmarks.int4_lane_scaling import _xorshift_vectors


class LaneScalingTests(unittest.TestCase):
    def test_exact_target_width_and_baugh_wooley_bias(self):
        expected = {8: (11, 0x790), 16: (12, 0xF90), 32: (13, 0x1F90)}
        for lanes in TARGET_LANES:
            width, bias = expected[lanes]
            self.assertEqual(accumulator_width(lanes), width)
            self.assertEqual(baugh_wooley_bias(width), bias)

    def test_linear_and_dadda_graphs_audit_at_all_scales(self):
        for lanes in TARGET_LANES:
            for schedule in ("linear", "dadda"):
                with self.subTest(lanes=lanes, schedule=schedule):
                    lines, manifest = generate_fused_heap(lanes, schedule)
                    audit = audit_fused_heap(lines, manifest)
                    self.assertTrue(all(bit["kind"] in ("partial_product", "constant")
                                        for bit in manifest["initial_bits"]))
                    initial_ids = {bit["id"] for bit in manifest["initial_bits"]}
                    compressor_ids = {
                        output for node in manifest["compressors"]
                        for output in (node["sum"], node["carry"]) if output
                    }
                    self.assertTrue(initial_ids.isdisjoint(compressor_ids))
                    self.assertEqual(audit["status"], "pass")
                    self.assertEqual(audit["lanes"], lanes)
                    self.assertEqual(audit["width"], accumulator_width(lanes))
                    observed_bias = sum(
                        1 << bit["column"] for bit in manifest["initial_bits"]
                        if bit["kind"] == "constant"
                    )
                    width = accumulator_width(lanes)
                    self.assertEqual(
                        observed_bias % (1 << width),
                        (lanes * baugh_wooley_bias(width)) % (1 << width),
                    )
                    self.assertGreater(audit["full_adders"], 0)
                    self.assertGreater(audit["compressors"], 0)
                    self.assertEqual(manifest["schedule"], schedule)

    def test_three_negative_tampers_rejected_at_all_scales(self):
        for lanes in TARGET_LANES:
            for schedule in ("linear", "dadda"):
                with self.subTest(lanes=lanes, schedule=schedule):
                    lines, manifest = generate_fused_heap(lanes, schedule)
                    with self.assertRaisesRegex(ValueError, "polarity/source mismatch"):
                        audit_fused_heap(tamper_partial_product_polarity(lines), manifest)
                    with self.assertRaisesRegex(ValueError, "carry"):
                        audit_fused_heap(lines, tamper_compressor_carry_weight(manifest))
                    with self.assertRaisesRegex(ValueError, "CPA output"):
                        audit_fused_heap(tamper_output_bit(lines, accumulator_width(lanes)), manifest)

    def test_xorshift_vectors_are_512_unique_and_reproducible(self):
        for lanes in TARGET_LANES:
            first = _xorshift_vectors(lanes)
            second = _xorshift_vectors(lanes)
            self.assertEqual(len(first), 512)
            self.assertEqual(len(set(first)), 512)
            self.assertEqual(first, second)

    def test_compositional_sat_proofs_at_all_widths_and_schedules(self):
        yosys = shutil.which("yosys")
        if not yosys:
            self.skipTest("Yosys is required for SAT proofs")
        for lanes in TARGET_LANES:
            for variant, schedule in (("fused_linear", "linear"), ("fused_dadda", "dadda")):
                with self.subTest(lanes=lanes, schedule=schedule):
                    top = f"formal_{variant}_{lanes}"
                    source = module_source(top, lanes, variant)
                    proof = run_compositional_proofs(lanes, schedule, source, yosys)
                    self.assertEqual(proof["formal_equivalence"], "formal-pass")
                    self.assertEqual(set(proof["proof_lemmas"]), {
                        "baugh_wooley_lane_identity", "full_adder_weighted_sum",
                        "half_adder_weighted_sum", "final_cpa_modulo_width",
                    })
                    self.assertEqual(proof["heap_audit"]["status"], "pass")

    def test_carry_save_proof_accepts_benchmark_top_names(self):
        yosys = shutil.which("yosys")
        if not yosys:
            self.skipTest("Yosys is required for equivalence checks")
        for lanes in TARGET_LANES:
            top = f"orcus_carry_save_{lanes}"
            candidate = module_source(top, lanes, "carry_save")
            reference = module_source("orcus_reference", lanes, "direct")
            with self.subTest(lanes=lanes):
                result = run_yosys_equivalence(candidate, reference, top, yosys)
                self.assertEqual(result["formal_equivalence"], "formal-pass")
                self.assertEqual(result["graph_audit"]["status"], "pass")

    def test_yosys_equivalence_for_direct_and_carry_save_at_all_scales(self):
        yosys = shutil.which("yosys")
        if not yosys:
            self.skipTest("Yosys is required for equivalence checks")
        for lanes in TARGET_LANES:
            reference = module_source("reference", lanes, "direct")
            for variant in ("direct", "carry_save"):
                with self.subTest(lanes=lanes, variant=variant):
                    top = f"equiv_{variant}_{lanes}"
                    candidate = module_source(top, lanes, variant)
                    result = run_yosys_equivalence(candidate, reference, top, yosys)
                    self.assertEqual(result["formal_equivalence"], "formal-pass")
                    if variant == "carry_save":
                        self.assertIn("compositional Yosys SAT", result["proof_method"])
                        self.assertEqual(result["graph_audit"]["status"], "pass")
                        self.assertEqual(
                            set(result["proof_lemmas"]),
                            {"carry_save_vector_invariant", "final_cpa_modulo_width"},
                        )
                        tampered = candidate.replace("cs_s_0_0 = ", "cs_s_0_0 = ~(", 1)
                        with self.assertRaisesRegex(ValueError, "regenerated audited tree"):
                            run_yosys_equivalence(tampered, reference, top, yosys)


if __name__ == "__main__":
    unittest.main()
