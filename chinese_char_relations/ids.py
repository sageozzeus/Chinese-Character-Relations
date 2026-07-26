# -*- coding: utf-8 -*-
"""Parse IDS (Ideographic Description Sequence) decomposition strings."""

from __future__ import annotations

# Hanzi decomposition operators → operand count
_IDS_ARITY: dict[str, int] = {
    "\u2ff0": 2,  # ⿰
    "\u2ff1": 2,  # ⿱
    "\u2ff2": 3,  # ⿲
    "\u2ff3": 3,  # ⿳
    "\u2ff4": 2,  # ⿴
    "\u2ff5": 2,  # ⿵
    "\u2ff6": 2,  # ⿶
    "\u2ff7": 2,  # ⿷
    "\u2ff8": 2,  # ⿸
    "\u2ff9": 2,  # ⿹
    "\u2ffa": 2,  # ⿺
    "\u2ffb": 2,  # ⿻
}

_UNKNOWN = frozenset({"?", "？", "\uff1f"})


def _read_operand(s: str, i: int) -> tuple[str | None, int]:
    if i >= len(s):
        return None, i
    ch = s[i]
    if ch in _UNKNOWN:
        return None, i
    if ch not in _IDS_ARITY:
        return ch, i + 1
    arity = _IDS_ARITY[ch]
    j = i + 1
    for _ in range(arity):
        _, j = _read_operand(s, j)
        if _ is None:
            return None, j
    return s[i:j], j


def immediate_operands(decomposition: str) -> list[str]:
    """Return top-level IDS operands (each may be one char or a nested IDS substring)."""
    decomp = (decomposition or "").strip()
    if not decomp or decomp in _UNKNOWN:
        return []
    if decomp[0] not in _IDS_ARITY:
        return []
    arity = _IDS_ARITY[decomp[0]]
    i = 1
    parts: list[str] = []
    for _ in range(arity):
        part, i = _read_operand(decomp, i)
        if part is None:
            return []
        parts.append(part)
    return parts


def decomposition_to_components(decomposition: str) -> list[str]:
    """
    Flatten decomposition into a list of component characters (HanziCraft-style).

    Unknown or missing decomposition yields an empty list.
    """
    parts = immediate_operands(decomposition)
    if not parts:
        return []
    out: list[str] = []
    for part in parts:
        if len(part) == 1 and part not in _IDS_ARITY:
            out.append(part)
        elif part and part[0] in _IDS_ARITY:
            out.extend(decomposition_to_components(part))
        else:
            for ch in part:
                if ch not in _IDS_ARITY and ch not in _UNKNOWN:
                    out.append(ch)
    return out
