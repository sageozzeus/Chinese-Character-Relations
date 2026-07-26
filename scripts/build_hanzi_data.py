#!/usr/bin/env python3
"""Build chinese_char_relations/data/hanzi_data.json from make-me-a-hanzi."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from chinese_char_relations.ids import decomposition_to_components  # noqa: E402

SOURCE_URL = (
    "https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt"
)
OUT_PATH = REPO_ROOT / "chinese_char_relations" / "data" / "hanzi_data.json"


def main() -> None:
    print(f"Fetching {SOURCE_URL} …")
    with urllib.request.urlopen(SOURCE_URL, timeout=120) as resp:
        raw = resp.read().decode("utf-8")

    data: dict[str, dict] = {}
    skipped = 0
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        ch = obj.get("character") or ""
        if len(ch) != 1:
            skipped += 1
            continue
        decomp = obj.get("decomposition") or ""
        components = decomposition_to_components(decomp)
        definition = (obj.get("definition") or "").strip()
        pinyin = obj.get("pinyin") or []
        if not isinstance(pinyin, list):
            pinyin = []
        pinyin = [str(p).strip() for p in pinyin if str(p).strip()]
        if not definition and not components and not pinyin:
            skipped += 1
            continue
        entry: dict = {}
        if definition:
            entry["definition"] = definition
        if pinyin:
            entry["pinyin"] = pinyin
        if components:
            entry["components"] = components
        if entry:
            data[ch] = entry

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"Wrote {len(data)} entries to {OUT_PATH} ({size_kb:.1f} KB)")
    print(f"Skipped {skipped} lines")


if __name__ == "__main__":
    main()
