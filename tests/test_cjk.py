# -*- coding: utf-8 -*-
"""Standalone tests for cjk helpers (no Anki required).

Run: python3 -m unittest tests.test_cjk -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Allow importing chinese_char_relations.cjk without Anki packages
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chinese_char_relations.cjk import (  # noqa: E402
    cjk_length,
    extract_cjk_chars,
    is_cjk_char,
    strip_html,
)


class TestCjk(unittest.TestCase):
    def test_is_cjk(self) -> None:
        self.assertTrue(is_cjk_char("好"))
        self.assertTrue(is_cjk_char("像"))
        self.assertFalse(is_cjk_char("a"))
        self.assertFalse(is_cjk_char("1"))
        self.assertFalse(is_cjk_char("，"))
        self.assertFalse(is_cjk_char(""))

    def test_extract_unique_order(self) -> None:
        self.assertEqual(extract_cjk_chars("好像好"), ["好", "像"])
        self.assertEqual(extract_cjk_chars("hello好world像"), ["好", "像"])

    def test_strip_html(self) -> None:
        self.assertEqual(strip_html("<b>好</b>"), "好")
        self.assertEqual(strip_html("好像"), "好像")

    def test_extract_after_html(self) -> None:
        self.assertEqual(extract_cjk_chars("<div>好像</div>"), ["好", "像"])

    def test_cjk_length(self) -> None:
        self.assertEqual(cjk_length("好像"), 2)
        self.assertEqual(cjk_length("好"), 1)
        self.assertEqual(cjk_length("hao好"), 1)


if __name__ == "__main__":
    unittest.main()
