# Manual testing

Run these after any change to indexing, rendering, or hooks. Use a small Chinese vocab deck with known compounds.

## Setup

1. Symlink or install the add-on; restart Anki (**Cmd+Q**, reopen)
2. Config fields to match your note type
3. **Tools → Chinese Character Relations…** → General → **Rebuild Index** — tooltip should show note/char counts

## Cases

### 0. Settings GUI

- Open **Tools → Chinese Character Relations…**
- **Expect:** dialog with General / Appearance / About tabs (not a JSON editor)
- Change a field, Save, rebuild when asked (or use **Rebuild Index** on General)
- Open **Tools → Add-ons → Chinese Character Relations → Config**
- **Expect:** same GUI dialog (not raw JSON)

### 1. Single-character card

- Review a note whose word is one char (e.g. 好)
- Flip to answer
- **Expect:** Related section lists multi-char words containing 好
- **Expect:** Current word 好 itself is not listed

### 2. Multi-character card

- Review 好像 (or similar)
- **Expect:** Groups headed by 好 and 像
- **Expect:** 好像 not listed under either group

### 3. No empty state noise

- Review a word whose characters appear nowhere else **and** have no bundled decomposition
- **Expect:** No Related box, no “0 related” message
- Review a rare char with decomposition but no deck relatives (if you have one in data)
- **Expect:** Components row only, no relatives scroller

### 3b. Character components

- Review **好** (or any char with known decomposition)
- **Expect:** Row `好 → 女 子` with pinyin above each tile; hover shows English gloss
- Review **好像** when only 好 has deck relatives
- **Expect:** Two character groups; 像 shows components even if relatives list is empty
- Turn off **Show character components** in General → Save → flip card
- **Expect:** Relatives UI unchanged from 0.1.0 (no decomposition row)

### 4. Front stays clean

- On question side, **Expect:** no Related panel
- After answer, go to next card question — **Expect:** previous panel gone

### 5. Suspended filter

- Suspend all cards of a related note
- Rebuild index
- Set `include_suspended` to `false` in Config (no rebuild required for this flag)
- Restart Anki or re-open reviewer so config reloads on next answer
- **Expect:** that note no longer appears
- Set back to `true` — **Expect:** it returns

### 6. Missing field names

- Set `fields.word` to a name that does not exist
- Rebuild
- **Expect:** no crash; optional tooltip about missing field on note types
- Review still works; Related simply absent

### 7. Rebuild picks up new notes

- Add a new compound sharing a character with an existing card
- Without rebuild, flip the related card — new word may be missing
- **Rebuild Index**
- **Expect:** new word appears in Related

### 8. Deck filter

- Set `decks` to one deck name only; rebuild
- **Expect:** relatives only from that deck

### 9. HTML in fields

- Note with `Word` containing `<b>好</b>` or sound tags wrapping text
- **Expect:** indexed/displayed as plain 好 (no raw tags in panel)

### 10. UI preview parity

- Open `preview/preview.html` (**Cmd+O**)
- Compare spacing/typography to Anki answer panel
- If you changed CSS in only one place, sync `PANEL_CSS` ↔ preview

## Regression smoke (2 minutes)

Rebuild → review one single-char → review one multi-char → next card front clear → Config open/save without error.
