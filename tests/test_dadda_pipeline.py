import unittest

from benchmarks.dadda_pipeline import (
    LANES, VECTOR_COUNT, build_control_miter, build_initial_heap_miter,
    build_stage_miter,
    build_sequential_miter, build_streaming_testbench,
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

    def test_initial_baugh_wooley_heap_matches_signed_mac(self):
        for lanes in LANES:
            for lane_index in range(lanes):
                with self.subTest(lanes=lanes, lane=lane_index):
                    source = build_initial_heap_miter(lanes, lane_index)
                    self.assertIn(
                        f"module orcus_dadda_initial_heap_miter_{lanes}_{lane_index}",
                        source,
                    )
                    self.assertIn("initial_heap_sum", source)
                    self.assertIn("extended_product", source)
                    self.assertIn("wire signed [7:0] signed_a", source)
                    self.assertIn("wire signed [7:0] signed_b", source)
                    self.assertIn("signed_product = signed_a * signed_b", source)
                    self.assertIn("assign bad = (initial_heap_sum != extended_product)", source)
                    self.assertIn(f"bias_{lane_index}_", source)


    def test_each_stage_has_independent_weighted_heap_sat_miter(self):
        for lanes in LANES:
            design = generate_dadda_pipelined(lanes)
            for stage in range(design.latency):
                with self.subTest(lanes=lanes, stage=stage):
                    source = build_stage_miter(lanes, stage)
                    self.assertIn(f"module orcus_dadda_stage_miter_{lanes}_{stage}", source)
                    self.assertIn("weighted_input", source)
                    self.assertIn("weighted_output", source)
                    self.assertIn("assign bad = (weighted_input != weighted_output)", source)
                    self.assertIn("^", source)
                    if stage == design.latency - 1:
                        self.assertIn("final_cpa", source)
                        self.assertIn("final_cpa != weighted_output", source)
                    else:
                        self.assertNotIn("final_cpa", source)

    def test_sequential_control_miter_checks_registered_output_boundary(self):
        for lanes in LANES:
            source, latency = build_control_miter(lanes)
            reference_depth = latency + 1
            self.assertIn(f"reg [{reference_depth - 1}:0] ref_valid_pipe;", source)
            self.assertIn(f"ref_valid_pipe[{reference_depth - 1}] <= ref_valid_pipe[{reference_depth - 2}];", source)
            self.assertIn(f"assign bad = (dut_valid != ref_valid_pipe[{reference_depth - 1}]);", source)
            self.assertIn(f"orcus_dadda_pipelined_{lanes} dut", source)
            self.assertIn("if (reset) ref_valid_pipe <= 0", source)
            self.assertNotIn("ref_data_pipe", source)
            self.assertEqual(build_sequential_miter(lanes), (source, latency))

    def test_dut_valid_depth_reference_depth_manifest_and_stream_latency_agree(self):
        for lanes in LANES:
            with self.subTest(lanes=lanes):
                design = generate_dadda_pipelined(lanes)
                latency = design.latency
                manifest_latency = design.manifest["latency_cycles"]
                control_source, control_latency = build_control_miter(lanes)
                stream_source, stream_latency = build_streaming_testbench(lanes)

                # L reduction-stage valid bits plus the separately registered
                # out_valid boundary form L+1 registered elements.  The input
                # sample reaches out_valid after L rising-edge intervals.
                self.assertEqual(manifest_latency, latency)
                self.assertEqual(control_latency, latency)
                self.assertEqual(stream_latency, latency)
                self.assertIn(f"reg [{latency - 1}:0] valid_pipe;", design.source)
                self.assertIn(f"out_valid <= valid_pipe[{latency - 1}];", design.source)
                dut_valid_depth = latency + int("output reg out_valid" in design.source)
                reference_depth = latency + 1
                self.assertEqual(dut_valid_depth, reference_depth)
                self.assertIn(f"reg [{latency}:0] ref_valid_pipe;", control_source)
                self.assertIn(f"ref_valid_pipe[{latency}]", control_source)
                self.assertIn(f"if (idx >= {latency})", stream_source)
                self.assertIn(f"vectors[idx - {latency}][2]", stream_source)
                self.assertIn(f"vectors[len(vectors) - {latency} + flush][2]", stream_source)

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
