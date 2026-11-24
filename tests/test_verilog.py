import unittest

from orcus.circuit import Circuit
from orcus.expression import gate, variable
from orcus.truth_table import TruthTable
from orcus.verilog import emit_verilog


class VerilogTests(unittest.TestCase):
    def test_verilog_uses_explicit_ports_and_internal_nodes(self):
        a = variable(0, TruthTable.variable(3, 0).bits)
        b = variable(1, TruthTable.variable(3, 1).bits)
        circuit = Circuit.from_expression(gate("XOR", (a, b), 255), 3)
        source = emit_verilog(circuit, "parity_fragment")
        self.assertIn("module parity_fragment(x0, x1, x2, y);", source)
        self.assertIn("assign y = n2;", source)
        self.assertIn("^", source)

    def test_invalid_module_name_rejected(self):
        a = variable(0, TruthTable.variable(1, 0).bits)
        circuit = Circuit.from_expression(a, 1)
        with self.assertRaises(ValueError):
            emit_verilog(circuit, "2bad")


if __name__ == "__main__":
    unittest.main()
