# -*- coding: utf-8 -*-
"""Build and query the character → notes inverted index."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

from aqt import mw
from aqt.utils import showInfo, tooltip

from .cjk import cjk_length, extract_cjk_chars, strip_html
from .defaults import merge_config

# Tried when the configured word field is missing from a note type
FALLBACK_WORD_FIELDS = (
    "Word",
    "Hanzi",
    "Expression",
    "Chinese",
    "汉字",
    "漢字",
    "Simplified",
    "Vocabulary",
    "Vocab",
    "Character",
    "Characters",
    "Front",
)


def _addon_package() -> str:
    return __name__.split(".")[0]


@dataclass
class RelatedEntry:
    note_id: int
    word: str
    pinyin: str
    meaning: str
    suspended: bool
    mature: bool = False


@dataclass
class BuildStats:
    scanned: int = 0
    indexed: int = 0
    chars: int = 0
    skip_no_field: int = 0
    skip_empty: int = 0
    skip_no_cjk: int = 0
    missing_field_models: set[str] = field(default_factory=set)
    used_word_field: str = ""
    resolved_fields_sample: set[str] = field(default_factory=set)


class CharIndex:
    """In-memory inverted index: CJK char → related note entries."""

    def __init__(self) -> None:
        self._index: dict[str, list[RelatedEntry]] = {}
        self.note_count: int = 0
        self.char_count: int = 0
        self.last_stats: BuildStats = BuildStats()

    def clear(self) -> None:
        self._index = {}
        self.note_count = 0
        self.char_count = 0

    def build(self, config: dict[str, Any], *, show_progress: bool = True) -> BuildStats:
        """Scan the collection and rebuild the index from scratch."""
        stats = BuildStats()
        col = mw.col
        if col is None:
            self.last_stats = stats
            return stats

        fields = config.get("fields") or {}
        word_field = (fields.get("word") or "Word").strip()
        pinyin_field = (fields.get("pinyin") or "Pinyin").strip()
        meaning_field = (fields.get("meaning") or "Meaning").strip()
        deck_names: list[str] = list(config.get("decks") or [])
        stats.used_word_field = word_field

        note_ids = self._find_note_ids(deck_names)
        stats.scanned = len(note_ids)
        active_nids = self._nids_with_active_card()
        mature_nids = self._nids_with_mature_card()
        new_index: dict[str, list[RelatedEntry]] = defaultdict(list)
        seen_per_char: dict[str, set[int]] = defaultdict(set)
        indexed_notes = 0

        total = len(note_ids)
        if show_progress and total:
            mw.progress.start(label="Building character relations…", max=total)

        try:
            for i, nid in enumerate(note_ids):
                if show_progress and total and i % 200 == 0:
                    mw.progress.update(
                        label=f"Building character relations… ({i}/{total})",
                        value=i,
                    )

                try:
                    note = col.get_note(nid)
                except Exception:
                    continue

                resolved_word = resolve_field(note, word_field, FALLBACK_WORD_FIELDS)
                if not resolved_word:
                    model_name = note.note_type()["name"]
                    stats.missing_field_models.add(model_name)
                    stats.skip_no_field += 1
                    continue

                stats.resolved_fields_sample.add(resolved_word)
                word = strip_html(note[resolved_word])
                if not word:
                    stats.skip_empty += 1
                    continue

                chars = extract_cjk_chars(word)
                if not chars:
                    stats.skip_no_cjk += 1
                    continue

                pinyin = ""
                meaning = ""
                rp = resolve_field(note, pinyin_field)
                rm = resolve_field(note, meaning_field)
                if rp:
                    pinyin = strip_html(note[rp])
                if rm:
                    meaning = strip_html(note[rm])

                suspended = nid not in active_nids
                mature = (not suspended) and (nid in mature_nids)
                entry = RelatedEntry(
                    note_id=nid,
                    word=word,
                    pinyin=pinyin,
                    meaning=meaning,
                    suspended=suspended,
                    mature=mature,
                )

                for ch in chars:
                    if nid in seen_per_char[ch]:
                        continue
                    seen_per_char[ch].add(nid)
                    new_index[ch].append(entry)

                indexed_notes += 1
        finally:
            if show_progress and total:
                mw.progress.finish()

        for ch, entries in new_index.items():
            entries.sort(key=self._sort_key)

        self._index = dict(new_index)
        self.note_count = indexed_notes
        self.char_count = len(self._index)
        stats.indexed = indexed_notes
        stats.chars = self.char_count
        self.last_stats = stats
        return stats

    def related_for(
        self,
        word: str,
        config: dict[str, Any],
        *,
        note_id: Optional[int] = None,
    ) -> list[tuple[str, list[RelatedEntry]]]:
        """
        Return related entries grouped by character for *word*.

        Groups preserve character order in *word*. Current note / headword excluded.
        """
        if not word or not self._index:
            return []

        include_suspended = bool(config.get("include_suspended", True))
        max_per_char = int(config.get("max_per_char", 8) or 8)
        min_len = int(config.get("candidate_min_length", 2) or 0)

        current = strip_html(word)
        current_cjk = "".join(extract_cjk_chars(current, unique=False))
        chars = extract_cjk_chars(current)
        if not chars:
            return []

        groups: list[tuple[str, list[RelatedEntry]]] = []
        for ch in chars:
            candidates = self._index.get(ch) or []
            filtered: list[RelatedEntry] = []
            for entry in candidates:
                if note_id is not None and entry.note_id == note_id:
                    continue
                if entry.word == current:
                    continue
                # Same CJK sequence (ignore punctuation / spacing drift)
                entry_cjk = "".join(extract_cjk_chars(entry.word, unique=False))
                if entry_cjk and entry_cjk == current_cjk:
                    continue
                if not include_suspended and entry.suspended:
                    continue
                if min_len and cjk_length(entry.word) < min_len:
                    continue
                filtered.append(entry)
                if len(filtered) >= max_per_char:
                    break
            if filtered:
                groups.append((ch, filtered))
        return groups

    @staticmethod
    def _sort_key(entry: RelatedEntry) -> tuple:
        # Mature first, then young/learning, suspended last; then shorter words
        if entry.suspended:
            status = 2
        elif entry.mature:
            status = 0
        else:
            status = 1
        return (status, cjk_length(entry.word), entry.word)

    @staticmethod
    def _find_note_ids(deck_names: list[str]) -> list[int]:
        col = mw.col
        assert col is not None

        if not deck_names:
            # Empty find_notes("") returns [] on some Anki builds — use SQL.
            try:
                ids = col.db.list("select id from notes")
                if ids:
                    return list(ids)
            except Exception:
                pass
            for query in ("*", "deck:*", ""):
                try:
                    ids = list(col.find_notes(query))
                    if ids:
                        return ids
                except Exception:
                    continue
            return []

        note_ids: set[int] = set()
        for name in deck_names:
            name = name.strip()
            if not name:
                continue
            note_ids.update(CharIndex._note_ids_for_deck(name))

        return list(note_ids)

    @staticmethod
    def _note_ids_for_deck(name: str) -> list[int]:
        """Resolve note IDs for one deck name (search, then SQL by deck id)."""
        col = mw.col
        assert col is not None
        safe = name.replace('"', '\\"')
        for query in (f'deck:"{safe}"', f"deck:{safe}"):
            try:
                ids = list(col.find_notes(query))
                if ids:
                    return ids
            except Exception:
                continue

        did = None
        try:
            did = col.decks.id(name, create=False)
        except Exception:
            if hasattr(col.decks, "id_for_name"):
                try:
                    did = col.decks.id_for_name(name)
                except Exception:
                    did = None
        if not did:
            return []
        try:
            return list(
                col.db.list(
                    "select distinct nid from cards where did = ? or odid = ?",
                    did,
                    did,
                )
            )
        except Exception:
            return []

    @staticmethod
    def _nids_with_active_card() -> set[int]:
        """Note IDs that have at least one non-suspended card (queue != -1)."""
        col = mw.col
        assert col is not None
        try:
            return set(col.db.list("select distinct nid from cards where queue != -1"))
        except Exception:
            return set()

    @staticmethod
    def _nids_with_mature_card() -> set[int]:
        """Note IDs with at least one active mature card (review, ivl >= 21 days)."""
        col = mw.col
        assert col is not None
        try:
            return set(
                col.db.list(
                    "select distinct nid from cards "
                    "where queue != -1 and type = 2 and ivl >= 21"
                )
            )
        except Exception:
            return set()


def resolve_field(
    note: Any,
    wanted: str,
    fallbacks: tuple[str, ...] = (),
) -> Optional[str]:
    """Match field by exact name, then case-insensitive, then fallbacks."""
    if not wanted and not fallbacks:
        return None
    try:
        keys = list(note.keys())
    except Exception:
        return None
    if wanted in keys:
        return wanted
    lower_map = {k.lower(): k for k in keys}
    if wanted:
        hit = lower_map.get(wanted.lower())
        if hit:
            return hit
    for name in fallbacks:
        if name in keys:
            return name
        hit = lower_map.get(name.lower())
        if hit:
            return hit
    return None


_index: Optional[CharIndex] = None


def get_index() -> CharIndex:
    global _index
    if _index is None:
        _index = CharIndex()
    return _index


def _format_stats(stats: BuildStats) -> str:
    return (
        f"Character Relations: indexed {stats.indexed} notes, {stats.chars} chars"
    )


def _explain_zero(stats: BuildStats, config: dict[str, Any]) -> None:
    """Show a clear dialog when nothing was indexed."""
    decks = config.get("decks") or []
    deck_line = "all decks" if not decks else ", ".join(decks[:5])
    fields = config.get("fields") or {}
    word_field = fields.get("word", "Word")

    lines = [
        "No notes were indexed.",
        "",
        f"Scanned: {stats.scanned} notes ({deck_line})",
        f"Configured word field: “{word_field}”",
        f"Skipped — field missing: {stats.skip_no_field}",
        f"Skipped — empty word: {stats.skip_empty}",
        f"Skipped — no Chinese characters: {stats.skip_no_cjk}",
    ]
    if stats.missing_field_models:
        models = ", ".join(sorted(stats.missing_field_models)[:8])
        lines.append(f"Note types without that field: {models}")
    if stats.resolved_fields_sample:
        used = ", ".join(sorted(stats.resolved_fields_sample))
        lines.append(f"Fields actually used: {used}")
    lines.extend(
        [
            "",
            "Fix: Tools → Character Relations → Settings…",
            "Set Word / Hanzi to the field that holds Chinese text,",
            "then Rebuild Index.",
        ]
    )
    showInfo("\n".join(lines))


def rebuild_index(*, show_progress: bool = True, notify: bool = True) -> None:
    """Rebuild the global index from current config."""
    if mw.col is None:
        return
    config = merge_config(mw.addonManager.getConfig(_addon_package()))
    idx = get_index()
    stats = idx.build(config, show_progress=show_progress)
    if notify:
        tooltip(_format_stats(stats), period=4000)
        if stats.indexed == 0:
            _explain_zero(stats, config)
