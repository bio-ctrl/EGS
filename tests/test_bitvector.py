import unittest

from orcus.bitvector import BitVectorGraph, DataNode, DataOutput, DataPort


class BitVectorGraphTests(unittest.TestCase):
    def test_addition_graph_exhaustively_matches_reference(self):
        graph = BitVectorGraph(
            inputs=(DataPort("a", 4), DataPort("b", 4)),
            nodes=(DataNode("total", "add", ("a", "b"), 5),),
            outputs=(DataOutput("sum", "total", 5),),
        )
        report = graph.verify_exhaustive(lambda x: {"sum": x["a"] + x["b"]})
        self.assertTrue(report.passed)
        self.assertTrue(report.exhaustive)
        self.assertEqual(report.vectors_checked, 256)
        self.assertEqual(graph.evaluate({"a": 15, "b": 1}), {"sum": 16})

    def test_mux_and_shared_node(self):
        graph = BitVectorGraph(
            inputs=(DataPort("sel", 1), DataPort("a", 4), DataPort("b", 4)),
            nodes=(
                DataNode("picked", "mux", ("sel", "a", "b"), 4),
                DataNode("masked", "and", ("picked", "a"), 4),
            ),
            outputs=(DataOutput("out", "masked", 4), DataOutput("also_picked", "picked", 4)),
        )
        self.assertEqual(graph.evaluate({"sel": 1, "a": 9, "b": 6}),
                         {"out": 9, "also_picked": 9})
        self.assertEqual(graph.metrics().max_fanout, 2)

    def test_width_wraparound_and_shift(self):
        graph = BitVectorGraph(
            inputs=(DataPort("a", 4), DataPort("amount", 3)),
            nodes=(DataNode("shifted", "shl", ("a", "amount"), 4),),
            outputs=(DataOutput("out", "shifted", 4),),
        )
        self.assertEqual(graph.evaluate({"a": 9, "amount": 2}), {"out": 4})

    def test_verilog_export(self):
        graph = BitVectorGraph(
            inputs=(DataPort("a", 4), DataPort("b", 4)),
            nodes=(DataNode("sum5", "add", ("a", "b"), 5),),
            outputs=(DataOutput("sum", "sum5", 5),),
        )
        source = graph.emit_verilog("adder4")
        self.assertIn("module adder4(a, b, sum);", source)
        self.assertIn("assign sum5 = a + b;", source)
        self.assertIn("assign sum = sum5;", source)

    def test_rejects_bad_widths_unknown_inputs_and_duplicate_names(self):
        with self.assertRaises(ValueError):
            BitVectorGraph((DataPort("a", 0),), (), (DataOutput("o", "a", 1),))
        with self.assertRaises(ValueError):
            BitVectorGraph((DataPort("a", 2),), (DataNode("n", "xor", ("a", "missing"), 2),),
                           (DataOutput("o", "n", 2),))
        with self.assertRaises(ValueError):
            BitVectorGraph((DataPort("a", 2),), (DataNode("a", "not", ("a",), 2),),
                           (DataOutput("o", "a", 2),))

    def test_verification_refuses_false_exhaustive_claim_when_too_wide(self):
        graph = BitVectorGraph(
            inputs=(DataPort("a", 16), DataPort("b", 16)),
            nodes=(DataNode("sum", "add", ("a", "b"), 16),),
            outputs=(DataOutput("out", "sum", 16),),
        )
        report = graph.verify_exhaustive(lambda x: {"out": (x["a"] + x["b"]) & 0xffff})
        self.assertFalse(report.passed)
        self.assertFalse(report.exhaustive)
        self.assertEqual(report.vectors_checked, 0)


if __name__ == "__main__":
    unittest.main()
