# Bug solutions — Chinese Character Relations

## Indexed 0 notes, 0 chars

**Symptom:** Rebuild Index tooltip shows `indexed 0 notes, 0 chars`.

**Root causes (in order of likelihood):**

1. **Wrong Word / Hanzi field** — defaults to `Word`, but many Chinese decks use `Hanzi`, `Expression`, `Chinese`, `汉字`, `Front`, etc. Notes are scanned then skipped.
2. **Empty note discovery** — on some Anki builds `col.find_notes("")` returns `[]`. Fixed by preferring `SELECT id FROM notes`.
3. **Deck filter** — Settings has specific decks checked that contain no matching notes.

**Fix shipped:**

- Discover all notes via SQL first (`select id from notes`), with search fallbacks (`*`, `deck:*`).
- Case-insensitive field match + fallbacks (`Hanzi`, `Expression`, …).
- When index stays empty, show a dialog with scan/skip counts and which note types lack the field.

**User action:** Tools → Character Relations → Settings… → set **Word / Hanzi** to the field that actually contains Chinese → Rebuild Index.

---

## Index OK but nothing on card back

**Symptom:** Rebuild reports hundreds of notes/chars, but flipping to the answer shows no Related panel.

**Root causes:**

1. **Reviewer field mismatch** — indexer accepted fallbacks (`Hanzi`, `Expression`, …) but the answer hook required an exact `Word` field and bailed out silently.
2. **Fragile `web.eval` injection** — Anki’s answer fade/DOM update can wipe content inserted in `reviewer_did_show_answer`.

**Fix shipped:**

- Reviewer uses the same `resolve_field` + fallbacks as the indexer.
- Primary injection via `gui_hooks.card_will_show` (`reviewAnswer`) — HTML appended before paint.
- `web.eval` kept only as a fallback if the panel id is missing.
- Exclude current note by `note_id` as well as headword text.

**User action:** Restart Anki (**Cmd+Q**), rebuild once, review a compound-rich character and flip.

---

## Raw JSON config opened instead of GUI

**Cause:** `setConfigAction` returned `False` or was not registered.

**Fix:** `open_config()` returns `True` after showing the dialog.

---

## Click related word opens broken Browser search

**Cause:** `dialogs.open("Browser", mw, search="nid:…")` passes a string; Anki does `search_for_terms(*search)`, which unpacks the string into characters.

**Fix:** Pass a one-element tuple: `search=(f"nid:{note_id}",)`.

---

## Multi-deck config misses some decks

**Cause:** Unquoted `deck:` fallback only ran when the whole `note_ids` set was still empty, so after the first deck contributed IDs, later decks that needed the fallback were skipped.

**Fix:** Resolve each deck independently via `_note_ids_for_deck` (quoted search → unquoted → SQL by deck id), then union the results.
