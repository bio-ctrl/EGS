import unittest
from benchmarks.ecp5_fpga_validation import wrapper_source
from orcus.lane_scaling import FPGA_TARGET_LANES, accumulator_width, module_source

class ECP5ValidationTests(unittest.TestCase):
    def test_supported_widths(self):
        self.assertEqual(FPGA_TARGET_LANES, (4, 8, 16, 32))
        self.assertEqual({n: accumulator_width(n) for n in FPGA_TARGET_LANES},
                         {4: 10, 8: 11, 16: 12, 32: 13})

    def test_registered_wrappers(self):
        for n in FPGA_TARGET_LANES:
            w = accumulator_width(n)
            for arch in ("direct", "fused_dadda"):
                with self.subTest(lanes=n, arch=arch):
                    src, top, _ = wrapper_source(n, arch)
                    self.assertIn(f"module {top}(input wire clk, output reg signed [{w-1}:0] result);", src)
                    self.assertIn("always @(posedge clk)", src)
                    self.assertIn("result <= core_y;", src)
                    self.assertEqual(src.count("reg [7:0] rng_"), n)

    def test_four_lane_architectures_generate(self):
        for arch in ("direct", "fused_dadda"):
            self.assertIn("module core(", module_source("core", 4, arch))

if __name__ == "__main__": unittest.main()
