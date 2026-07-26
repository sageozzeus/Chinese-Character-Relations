# -*- coding: utf-8 -*-
"""Tests for IDS decomposition parsing."""

import unittest

from chinese_char_relations.ids import decomposition_to_components, immediate_operands


class TestIds(unittest.TestCase):
    def test_hao(self) -> None:
        self.assertEqual(decomposition_to_components("⿰女子"), ["女", "子"])
        self.assertEqual(immediate_operands("⿰女子"), ["女", "子"])

    def test_unknown(self) -> None:
        self.assertEqual(decomposition_to_components("？"), [])
        self.assertEqual(decomposition_to_components(""), [])
        self.assertEqual(decomposition_to_components("?"), [])

    def test_nested(self) -> None:
        # ⿱ over 木 and ⿰木木 → three 木
        decomp = "⿱木⿰木木"
        self.assertEqual(decomposition_to_components(decomp), ["木", "木", "木"])


if __name__ == "__main__":
    unittest.main()
