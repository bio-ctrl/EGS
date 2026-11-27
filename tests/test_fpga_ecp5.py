import unittest

from benchmarks.fpga_ecp5 import (
    DEVICE, TARGET_LANES, VARIANTS, build_wrapper_source,
    parse_nextpnr_report, parse_yosys_netlist,
)
from orcus.lane_scaling import accumulator_width


class ECP5BenchmarkTests(unittest.TestCase):
    def test_target_matrix_and_widths(self):
        self.assertEqual(TARGET_LANES, (4, 8, 16, 32))
        self.assertEqual(VARIANTS, ("direct", "fused_dadda"))
        self.assertEqual(DEVICE, "LFE5U-85F-6BG381C")
        self.assertEqual([accumulator_width(n) for n in TARGET_LANES], [10, 11, 12, 13])

    def test_clocked_wrappers_have_identical_register_boundary(self):
        for lanes in TARGET_LANES:
            width = accumulator_width(lanes)
            for variant in VARIANTS:
                with self.subTest(lanes=lanes, variant=variant):
                    source = build_wrapper_source(lanes, variant)
                    self.assertIn("input wire clk", source)
                    self.assertIn(f"output reg signed [{width - 1}:0] y", source)
                    self.assertEqual(source.count("always @(posedge clk)"), 1)
                    self.assertIn(f"module orcus_{variant}_{lanes}_core", source)
                    self.assertIn("y <= core_y;", source)
                    for lane in range(lanes):
                        self.assertIn(f"a{lane}_q <= a{lane};", source)
                        self.assertIn(f"b{lane}_q <= b{lane};", source)

    def test_yosys_mapped_resource_counts(self):
        netlist = {
            "modules": {
                "orcus_fpga_top": {
                    "cells": {
                        "l0": {"type": "LUT4"},
                        "l1": {"type": "LUT4"},
                        "c0": {"type": "CCU2C"},
                        "f0": {"type": "TRELLIS_FF"},
                        "m0": {"type": "MULT18X18D"},
                    }
                }
            }
        }
        parsed = parse_yosys_netlist(netlist)
        self.assertEqual(parsed["lut4"], 2)
        self.assertEqual(parsed["ccu2c"], 1)
        self.assertEqual(parsed["carry_stages"], 2)
        self.assertEqual(parsed["flip_flops"], 1)
        self.assertEqual(parsed["mult18x18d"], 1)

    def test_nextpnr_report_fmax_and_utilization(self):
        report = {
            "utilization": {
                "TRELLIS_COMB": {"used": 20, "available": 83640},
                "CCU2C": {"used": 3, "available": 20800},
                "TRELLIS_FF": {"used": 18, "available": 83640},
            },
            "fmax": {"clk": {"achieved": 123.4, "constraint": 100.0}},
        }
        parsed = parse_nextpnr_report(report)
        self.assertEqual(parsed["achieved_fmax_mhz"], 123.4)
        self.assertEqual(parsed["constraint_mhz"], 100.0)
        self.assertTrue(parsed["timing_met"])
        self.assertEqual(parsed["utilization"]["CCU2C"]["used"], 3)

    def test_nextpnr_report_requires_clock_domain(self):
        with self.assertRaisesRegex(ValueError, "timing domain"):
            parse_nextpnr_report({
                "utilization": {},
                "fmax": {},
            })


if __name__ == "__main__":
    unittest.main()
