# -*- coding: utf-8 -*-
"""Bundled character decomposition / pinyin / definitions (make-me-a-hanzi derived)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

_DATA: dict[str, dict[str, Any]] | None = None
_DATA_PATH = Path(__file__).resolve().parent / "data" / "hanzi_data.json"


@dataclass(frozen=True)
class HanziEntry:
    definition: str
    pinyin: list[str]
    components: list[str]

    def display_pinyin(self) -> str:
        if not self.pinyin:
            return ""
        return self.pinyin[0]


def _load() -> dict[str, dict[str, Any]]:
    global _DATA
    if _DATA is not None:
        return _DATA
    if not _DATA_PATH.is_file():
        _DATA = {}
        return _DATA
    with _DATA_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    _DATA = raw if isinstance(raw, dict) else {}
    return _DATA


def get(ch: str) -> Optional[HanziEntry]:
    """Lookup one character, or None if not in bundled data."""
    if not ch or len(ch) != 1:
        return None
    row = _load().get(ch)
    if not row:
        return None
    definition = str(row.get("definition") or "").strip()
    pinyin_raw = row.get("pinyin") or []
    pinyin = [str(p) for p in pinyin_raw if p] if isinstance(pinyin_raw, list) else []
    comp_raw = row.get("components") or []
    components = [str(c) for c in comp_raw if c] if isinstance(comp_raw, list) else []
    if not definition and not pinyin and not components:
        return None
    return HanziEntry(definition=definition, pinyin=pinyin, components=components)


def has_decomp_or_meta(ch: str) -> bool:
    """True if we can show a decomposition row or hover text for *ch*."""
    entry = get(ch)
    if not entry:
        return False
    return bool(entry.components or entry.definition or entry.pinyin)


def clear_cache_for_tests() -> None:
    global _DATA
    _DATA = None
