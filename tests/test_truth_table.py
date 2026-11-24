import unittest

from orcus.truth_table import TruthTable, variables


class TruthTableTests(unittest.TestCase):
    def test_three_variable_encoding(self):
        a, b, c = variables(3)
        self.assertEqual(a.binary(), "00001111")
        self.assertEqual(b.binary(), "00110011")
        self.assertEqual(c.binary(), "01010101")

    def test_bitwise_operations_are_masked(self):
        a, b, _ = variables(3)
        self.assertEqual((a & b).binary(), "00000011")
        self.assertEqual((a | b).binary(), "00111111")
        self.assertEqual((a ^ b).binary(), "00111100")
        self.assertEqual((~a).binary(), "11110000")

    def test_from_callable_and_round_trip(self):
        table = TruthTable.from_callable(3, lambda a, b, c: a ^ b ^ c)
        self.assertEqual(TruthTable.from_binary(3, table.binary()), table)
        self.assertEqual(TruthTable.from_int(3, table.bits), table)

    def test_invalid_width_is_rejected(self):
        with self.assertRaises(ValueError):
            TruthTable(3, 256)
        with self.assertRaises(ValueError):
            TruthTable.from_binary(3, "101")

    def test_non_boolean_assignment_is_rejected(self):
        table = TruthTable.variable(3, 0)
        with self.assertRaises(ValueError):
            table.output((0, 2, 1))

    def test_input_count_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            _ = TruthTable.constant(2, True) & TruthTable.constant(3, True)


if __name__ == "__main__":
    unittest.main()
