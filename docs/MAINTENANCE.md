# Maintenance Guide — Chinese Character Relations

This document is the source of truth for maintaining and extending the add-on. Read this before changing behavior.

## What the add-on does

During review, when the **answer** is shown, the add-on:

1. Reads the current note’s configured **word** field
2. Extracts unique CJK characters (Unicode ideographs)
3. Looks up other notes in an in-memory inverted index that contain those characters
4. Injects a **Related** HTML panel under the card (does not edit notes or templates)

If there are no relations, nothing is injected (no empty box).

```
profile open / sync / Tools→Rebuild
        │
        ▼
  indexer.build()  ──►  char → [RelatedEntry, ...]   (RAM only)
        │
reviewer_did_show_answer
        │
        ▼
  related_for(word) → render_panel() → webview.eval(append)
        │
reviewer_did_show_question
        │
        ▼
  remove #char-relations-panel
```

## Repository layout

```
hanzi-relatives/
├── chinese_char_relations/     # THE add-on (this folder is what Anki loads)
│   ├── __init__.py             # Hooks + Tools menu + Config action
│   ├── manifest.json           # Offline install identity
│   ├── about_meta.py           # Version, author links, changelog (About tab)
│   ├── config.json             # Default config (Anki merges user meta.json)
│   ├── config.md               # Short help text
│   ├── config_dialog.py        # GUI settings (General / Appearance / About)
│   ├── cjk.py                  # CJK extract / HTML strip
│   ├── indexer.py              # Build + query inverted index
│   ├── render.py               # HTML/CSS for Related panel
│   └── reviewer.py             # Answer/question hooks + injection
├── preview/
│   ├── preview.html            # Browser UI sandbox — card panel (NOT shipped in .ankiaddon)
│   └── config-preview.html     # Settings dialog mock — sync with config_dialog.py
├── docs/
│   ├── MAINTENANCE.md          # This file (dev setup, architecture, publish)
│   ├── TESTING.md              # Manual QA checklist
│   └── BUG_SOLUTIONS.md        # Known fixes / Qt gotchas
├── LICENSE                     # MIT
└── README.md                   # End-user install & usage
```

## Development setup (symlink)

Do **not** copy the add-on folder into `addons21` on every change. Symlink once:

```bash
./scripts/link-anki-addon.sh
# or:
ln -s "/ABS/PATH/TO/repo/chinese_char_relations" \
  "$HOME/Library/Application Support/Anki2/addons21/chinese_char_relations"
```

Then: edit in this repo → quit Anki fully (**Cmd+Q**) → reopen → flip a card.

If a real folder already exists at that path, rename or remove it before creating the symlink.

Anki loads Python at startup. There is **no hot reload**.

## UI preview (no Anki)

- **Card panel:** [`preview/preview.html`](../preview/preview.html) — answer-side Relatives UI (**Cmd+O** in Finder, or open via a local server)
- **Settings dialog:** [`preview/config-preview.html`](../preview/config-preview.html) — mock of **Tools → Character Relations…** (tabs: General / Appearance / About)

Edit `.char-relations*` CSS in `preview.html`, then copy the same rules into `chinese_char_relations/render.py` (`PANEL_CSS`). Tweak settings layout/copy in `config-preview.html`, then mirror in `config_dialog.py`.

## Module map (change guide)

| Want to change… | Edit |
| --- | --- |
| Which Unicode counts as “Chinese” | `cjk.py` → `_CJK_RANGES`, `is_cjk_char` |
| How fields/decks are scanned | `indexer.py` → `CharIndex.build` |
| Sort / filter / caps of relatives | `indexer.py` → `related_for`, `_sort_key` |
| Panel markup / CSS | `render.py` → `PANEL_CSS`, `render_panel` + sync `preview/preview.html` |
| When panel appears / clears | `reviewer.py` → `on_show_answer`, `on_show_question` |
| Click related word → Browser | `browser.py` + `pycmd` in `render.py` PANEL_JS |
| Settings GUI (decks, fields, Appearance, About) | `config_dialog.py` + `defaults.py` + `about_meta.py` |
| Version / About links / changelog | `about_meta.py` (keep preview About tab in sync) |
| Panel CSS variables from Appearance tab | `render.py` → `_css_var_block` / `ui` config |
| Menu / rebuild / Config button wiring | `__init__.py` |
| Defaults users get on first install | `config.json` + `config.md` |

## Settings GUI

Users never edit JSON. The dialog is opened from:

- **Tools → Character Relations…** (opens settings GUI)
- **Tools → Add-ons → Config** (via `mw.addonManager.setConfigAction`)

Tabs: **General**, **Appearance**, **About** (read-only metadata from `about_meta.py`).

`open_config()` must **not** return `False`, or Anki falls back to the raw JSON editor.

On Save: `writeConfig` → optional rebuild prompt. Deck/field changes need a rebuild; `include_suspended` applies on next answer without rebuild.

## Config contract

Loaded with:

```python
mw.addonManager.getConfig("chinese_char_relations")
```

(Anki resolves the package from `__name__` via `split(".")[0]`.)

User edits are stored in the add-on’s `meta.json` under the profile’s `addons21` folder (or inside the linked folder’s `meta.json` when using a symlink). **Never commit secrets**; `meta.json` is user-local.

| Key | Type | Behavior |
| --- | --- | --- |
| `decks` | `string[]` | Empty → `find_notes("")`. Else union of `deck:"Name"` searches. |
| `fields.word` | string | Required per note type; missing → skip note. |
| `fields.pinyin` | string | Optional; blank if field absent. |
| `max_per_char` | int | Slice after filters. |
| `include_suspended` | bool | Applied at **lookup** (no rebuild needed). |
| `candidate_min_length` | int | Min CJK char count on candidate words. |
| `show_only_on_back` | bool | On = answer only; off = front + back. Legacy `show_on_answer_only` still read. |

After changing `decks` or `fields`, users must **Rebuild Index**.

## Index algorithm (keep this shape)

```
for each note in target decks:
  word = strip_html(note[word_field])
  chars = unique CJK in word (order preserved)
  entry = {note_id, word, pinyin, meaning, suspended}
  for ch in chars:
    index[ch].append(entry)   # dedupe by note_id
sort each list: (status, cjk_length, word) — status: mature (0), active learning (1), suspended (2)
```

**Suspended:** note has no card with `queue != -1` (built via one SQL `distinct nid` query, not per-note card fetches).

**Lookup:** for each char in current word → exclude current note/word → apply suspended + min length → sort by `_sort_key` → take first `max_per_char`.

Do **not** run `find_notes` / full collection scans inside `on_show_answer`. That must stay O(chars × max_per_char).

## Reviewer injection rules

- Prefer `#qa` as parent; fall back to `document.body`
- Always remove previous `#char-relations-panel` and `#char-relations-style` before inject / on question
- Escape all note text with `html.escape` in `render.py`
- Never rewrite card templates or note fields in MVP

JS is sent via `mw.reviewer.web.eval(...)`. HTML is passed through `json.dumps` so quotes/newlines are safe.

## UI iteration workflow

1. Open `preview/preview.html` with **Cmd+O**
2. Tweak `.char-relations*` CSS until it looks right
3. Copy those rules into `render.py` → `PANEL_CSS`
4. Restart Anki and verify under a real card (night mode, custom templates)

Keep the comment in both files: **KEEP IN SYNC**.

## Hooks used (Anki 23.10+)

| Hook | Purpose |
| --- | --- |
| `gui_hooks.main_window_did_init` | Install Tools submenu once |
| `gui_hooks.profile_did_open` | Build index (silent) |
| `gui_hooks.sync_did_finish` | Rebuild index + tooltip |
| `gui_hooks.reviewer_did_show_answer` | Inject panel |
| `gui_hooks.reviewer_did_show_question` | Clear panel |

Legacy `anki.hooks.addHook` is intentionally unused.

## Safe failure modes

| Situation | Behavior |
| --- | --- |
| Word field missing on a note type | Skip those notes; one tooltip listing model names |
| Empty word / no CJK | Skip |
| Empty index / no relations | Inject nothing |
| Collection not open | Rebuild no-ops |
| HTML in fields | Stripped for indexing; escaped for display |

## Performance notes

- Index lives only in RAM (`CharIndex` singleton). Tens of thousands of notes is fine.
- Rebuild shows `mw.progress` and updates every 200 notes.
- Suspended set is one SQL query at build start.
- If rebuild feels slow on huge collections: restrict `decks` in config before optimizing further.

## Phase 2 ideas (not implemented)

Do not start these until MVP is stable:

1. Click row → `pycmd` → Browser `nid:…`
2. Sort: unsuspended / mature first; frequency if available
3. Optional note-type allowlist
4. Optional write into a Related field (for AnkiMobile sync)
5. CEDICT fallback for chars with no deck relatives

Extension points already shaped for this:

- `RelatedEntry` dataclass — add fields without breaking render
- `related_for` — sorting/filtering lives in one place
- `render_panel` — can add `data-nid` attributes later

## Publishing to AnkiWeb

1. Ensure `preview/` is **not** inside the zip (it isn’t under `chinese_char_relations/`)
2. Delete `__pycache__`
3. From inside `chinese_char_relations/`:

   ```bash
   zip -r ../chinese_char_relations.ankiaddon *
   ```

4. Upload at https://ankiweb.net/shared/addons/
5. AnkiWeb assigns a numeric folder id on install; `manifest.json` `package` matters mainly for offline `.ankiaddon` installs
6. After the listing exists, set `URL_ANKIWEB` in `about_meta.py` to  
   `https://ankiweb.net/shared/info/<id>` so the About tab shows **AnkiWeb page** and **Rate / review**. Mirror that in `preview/config-preview.html`.

Update the AnkiWeb description when behavior changes. Bump the human version in **`about_meta.py`** (`ADDON_VERSION` + prepend a `CHANGELOG` entry) whenever you ship, and match the AnkiWeb listing version string.

Packaging reminder: the zip must contain files at the **top level** of the archive (not a wrapping folder). `preview/`, `docs/`, and tests stay outside `chinese_char_relations/` so they are not included.

## Automated tests (no Anki)

CJK helpers are covered by unittest (does not need Anki/`aqt`):

```bash
cd /Users/urfan/Desktop/apps-websites/hanzi-relatives
python3 -m unittest tests.test_cjk -v
```

`__init__.py` guards `aqt` imports so the package can be imported outside Anki for these tests. Indexer/reviewer still require a live Anki session (see [`TESTING.md`](TESTING.md)).

## Debugging on Mac

1. Start Anki from Terminal to see stdout/stderr:

   ```bash
   /Applications/Anki.app/Contents/MacOS/anki
   ```

2. Or use **Tools → Add-ons → View Files** to confirm the symlink target
3. Debug Console: paste small probes, e.g. inspect index size after load

## Common pitfalls

- **Edited code but no change** — Anki still running old process; fully quit with **Cmd+Q**
- **Symlink vs copy** — a real folder in `addons21` shadows the repo; remove it and re-link
- **Field names** — Chinese decks often use `Hanzi` / `Expression`; config must match exactly (case-sensitive)
- **CSS drift** — preview and `PANEL_CSS` diverge; always copy both ways when changing styles
- **`min_point_version`** — `manifest.json` targets 23.10+; lowering it may load on older Anki but hooks might differ

## File ownership checklist when touching code

1. Change the smallest module that owns the behavior (table above)
2. If CSS: update `render.py` **and** `preview/preview.html`
3. If config keys: update `config.json`, `config.md`, and this doc (user-facing defaults stay in `config.md` / the settings GUI)
4. Run through [`TESTING.md`](TESTING.md) for the affected cases
5. Rebuild index in Anki after field/deck changes
