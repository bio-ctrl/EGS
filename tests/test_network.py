import unittest

from orcus.expression import gate, variable
from orcus.network import CircuitNetwork
from orcus.network_verilog import emit_network_verilog
from orcus.truth_table import TruthTable


class CircuitNetworkTests(unittest.TestCase):
    def test_common_logic_is_shared_across_outputs(self):
        a = variable(0, TruthTable.variable(3, 0).bits)
        b = variable(1, TruthTable.variable(3, 1).bits)
        c = variable(2, TruthTable.variable(3, 2).bits)
        shared = gate("AND", (a, b), 255)
        network = CircuitNetwork.from_expressions({
            "ab": shared,
            "ab_or_c": gate("OR", (shared, c), 255),
            "ab_xor_c": gate("XOR", (shared, c), 255),
        }, 3)
        expected = {
            "ab": TruthTable.from_callable(3, lambda x, y, z: x & y),
            "ab_or_c": TruthTable.from_callable(3, lambda x, y, z: (x & y) | z),
            "ab_xor_c": TruthTable.from_callable(3, lambda x, y, z: (x & y) ^ z),
        }
        self.assertTrue(network.verify(expected))
        self.assertEqual(sum(node.op == "AND" for node in network.nodes), 1)
        self.assertEqual(network.metrics().unique_gate_count, 3)
        self.assertEqual(network.evaluate((1, 1, 0)), {"ab": 1, "ab_or_c": 1, "ab_xor_c": 1})

    def test_invalid_boolean_assignment_is_rejected(self):
        a = variable(0, TruthTable.variable(2, 0).bits)
        network = CircuitNetwork.from_expressions({"out": a}, 2)
        with self.assertRaises(ValueError):
            network.evaluate((0, -1))

    def test_multoutput_verilog_mentions_each_output(self):
        a = variable(0, TruthTable.variable(2, 0).bits)
        b = variable(1, TruthTable.variable(2, 1).bits)
        network = CircuitNetwork.from_expressions({"both": gate("AND", (a, b), 15), "either": gate("OR", (a, b), 15)}, 2)
        source = emit_network_verilog(network, "two_outputs")
        self.assertIn("output both, either;", source)
        self.assertIn("assign both =", source)
        self.assertIn("assign either =", source)


if __name__ == "__main__":
    unittest.main()
