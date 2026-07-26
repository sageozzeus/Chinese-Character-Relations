# -*- coding: utf-8 -*-
"""Tests for bundled hanzi data loader."""

import unittest
from pathlib import Path
from unittest import mock

from chinese_char_relations import hanzi_data

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "hanzi_data_mini.json"


class TestHanziData(unittest.TestCase):
    def setUp(self) -> None:
        hanzi_data.clear_cache_for_tests()

    def tearDown(self) -> None:
        hanzi_data.clear_cache_for_tests()

    def test_get_from_fixture(self) -> None:
        with mock.patch.object(hanzi_data, "_DATA_PATH", FIXTURE):
            hanzi_data.clear_cache_for_tests()
            entry = hanzi_data.get("好")
            self.assertIsNotNone(entry)
            assert entry is not None
            self.assertEqual(entry.components, ["女", "子"])
            self.assertEqual(entry.display_pinyin(), "hǎo")
            self.assertIn("good", entry.definition)

    def test_missing_char(self) -> None:
        with mock.patch.object(hanzi_data, "_DATA_PATH", FIXTURE):
            hanzi_data.clear_cache_for_tests()
            self.assertIsNone(hanzi_data.get("像"))


if __name__ == "__main__":
    unittest.main()
