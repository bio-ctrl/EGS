import unittest

from benchmarks.dadda_pipeline import (
    LANES, VECTOR_COUNT, build_sequential_miter, build_streaming_testbench,
    _vectors,
)
from orcus.dadda_pipeline import generate_dadda_pipelined
from orcus.lane_scaling import accumulator_width


class DaddaPipelineGeneratorTests(unittest.TestCase):
    def test_all_lane_configurations_have_complete_stage_boundaries(self):
        for lanes in LANES:
            with self.subTest(lanes=lanes):
                design = generate_dadda_pipelined(lanes)
                self.assertEqual(design.width, accumulator_width(lanes))
                self.assertEqual(design.latency, len(design.stage_targets))
                self.assertEqual(len(design.manifest["stage_boundaries"]), design.latency)
                self.assertGreater(design.latency, 0)
                for stage, boundary in enumerate(design.manifest["stage_boundaries"]):
                    self.assertEqual(boundary["stage"], stage)
                    self.assertEqual(
                        boundary["registered_bit_count"],
                        sum(len(column) for column in boundary["registered_heap"]),
                    )
                    expected = [
                        [f"st{stage}_q_{token}" for token in column]
                        for column in boundary["output_heap"]
                    ]
                    self.assertEqual(boundary["registered_heap"], expected)

    def test_pipeline_interface_reset_and_latency_metadata(self):
        for lanes in LANES:
            design = generate_dadda_pipelined(lanes)
            self.assertIn(f"module orcus_dadda_pipelined_{lanes}(", design.source)
            self.assertIn("input wire reset", design.source)
            self.assertIn("input wire in_valid", design.source)
            self.assertIn("output reg out_valid", design.source)
            self.assertIn("if (reset)", design.source)
            self.assertIn(f"localparam integer LATENCY = {design.latency};", design.source)
            self.assertIn(f"out_valid <= valid_pipe[{design.latency - 1}];", design.source)
            self.assertIn("one input transaction per cycle", design.manifest["throughput"])

    def test_sequential_miter_aligns_reference_at_latency(self):
        for lanes in LANES:
            source, latency = build_sequential_miter(lanes)
            self.assertIn(f"ref_valid_pipe[{latency}]", source)
            self.assertIn(f"ref_data_pipe[{latency}]", source)
            self.assertIn("dut_valid != ref_valid_pipe", source)
            self.assertIn("dut_data != ref_data_pipe", source)

    def test_streaming_testbench_has_512_back_to_back_vectors(self):
        for lanes in LANES:
            source, latency = build_streaming_testbench(lanes)
            self.assertEqual(VECTOR_COUNT, 512)
            self.assertIn("stream mismatch", source)
            self.assertIn("flush mismatch", source)
            self.assertIn("in_valid = 1'b1", source)
            self.assertIn("in_valid = 1'b0", source)
            self.assertIn("stale transaction leaked after reset", source)
            self.assertGreater(latency, 0)

    def test_reference_vectors_are_signed_and_width_bounded(self):
        for lanes in LANES:
            width = accumulator_width(lanes)
            lower, upper = -(1 << (width - 1)), (1 << (width - 1)) - 1
            vectors = _vectors(lanes)
            self.assertEqual(len(vectors), VECTOR_COUNT)
            self.assertTrue(all(lower <= expected <= upper for _, _, expected in vectors))


if __name__ == "__main__":
    unittest.main()
