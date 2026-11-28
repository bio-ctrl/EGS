import unittest

from orcus.circuit import Circuit, measure_circuit
from orcus.expression import gate, variable
from orcus.truth_table import TruthTable


class CircuitTests(unittest.TestCase):
    def test_expression_compiles_and_verifies(self):
        a = variable(0, TruthTable.variable(3, 0).bits)
        b = variable(1, TruthTable.variable(3, 1).bits)
        expr = gate("XOR", (a, b), 255)
        circuit = Circuit.from_expression(expr, 3)
        expected = TruthTable.from_callable(3, lambda x, y, z: x ^ y)
        self.assertTrue(circuit.verify(expected))
        self.assertEqual(circuit.evaluate((1, 0, 1)), 1)

    def test_common_subexpression_is_shared_in_ir(self):
        a = variable(0, TruthTable.variable(3, 0).bits)
        b = variable(1, TruthTable.variable(3, 1).bits)
        shared = gate("XOR", (a, b), 255)
        expr = gate("AND", (shared, shared), 255)
        circuit = Circuit.from_expression(expr, 3)
        self.assertEqual(sum(node.op == "XOR" for node in circuit.nodes), 1)

    def test_non_boolean_assignment_is_rejected(self):
        a = variable(0, TruthTable.variable(3, 0).bits)
        circuit = Circuit.from_expression(a, 3)
        with self.assertRaises(ValueError):
            circuit.evaluate((0, 3, 1))

    def test_metrics_are_truthful_for_small_circuit(self):
        a = variable(0, TruthTable.variable(3, 0).bits)
        b = variable(1, TruthTable.variable(3, 1).bits)
        expr = gate("AND", (a, b), 255)
        metrics = measure_circuit(Circuit.from_expression(expr, 3))
        self.assertEqual(metrics.gate_count, 1)
        self.assertEqual(metrics.logic_depth, 1)
        self.assertEqual(metrics.max_fanout, 1)
        self.assertAlmostEqual(metrics.output_one_density, 0.25)


if __name__ == "__main__":
    unittest.main()
