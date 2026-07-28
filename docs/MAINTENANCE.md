# Maintenance Guide — Chinese Character Relations

This document is the source of truth for maintaining and extending the add-on. Read this before changing behavior.

## What the add-on does

During review, when the **answer** is shown, the add-on:

1. Reads the current note’s configured **word** field
2. Extracts unique CJK characters (Unicode ideographs)
3. For each character: optional **decomposition** from bundled `hanzi_data.json`; **related words** from an in-memory inverted index built from your decks
4. Injects a **Relatives** HTML panel under the card (does not edit notes or templates)

If there are no relatives and no decomposition for any character in the word, nothing is injected.

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
│   ├── ids.py                  # IDS decomposition parsing (build + tests)
│   ├── hanzi_data.py           # Load bundled hanzi_data.json
│   ├── data/hanzi_data.json    # Shipped character metadata (regenerate via scripts/)
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
- **Settings dialog:** [`preview/config-preview.html`](../preview/config-preview.html) — mock of **Tools → Chinese Character Relations…** (tabs: General / Appearance / About)

Edit `.char-relations*` CSS in `preview.html`, then copy the same rules into `chinese_char_relations/render.py` (`PANEL_CSS`). Tweak settings layout/copy in `config-preview.html`, then mirror in `config_dialog.py`.

## Module map (change guide)

| Want to change… | Edit |
| --- | --- |
| Which Unicode counts as “Chinese” | `cjk.py` → `_CJK_RANGES`, `is_cjk_char` |
| How fields/decks are scanned | `indexer.py` → `CharIndex.build` |
| Sort / filter / caps of relatives | `indexer.py` → `related_for`, `_sort_key` |
| Panel markup / CSS | `render.py` → `PANEL_CSS`, `render_panel` + sync `preview/preview.html` |
| Character decomposition data | `data/hanzi_data.json`; regen: `python3 scripts/build_hanzi_data.py` |
| Bundled dict loader | `hanzi_data.py` |
| When panel appears / clears | `reviewer.py` → `on_show_answer`, `on_show_question` |
| Click related word → Browser | `browser.py` + `pycmd` in `render.py` PANEL_JS |
| Settings GUI (decks, fields, Appearance, About) | `config_dialog.py` + `defaults.py` + `about_meta.py` |
| Version / About links / changelog | `about_meta.py` (keep preview About tab in sync) |
| Panel CSS variables from Appearance tab | `render.py` → `_css_var_block` / `ui` config |
| Menu / rebuild / Config button wiring | `__init__.py` |
| Defaults users get on first install | `config.json` + `config.md` |

## Settings GUI

Users never edit JSON. The dialog is opened from:

- **Tools → Chinese Character Relations…** (opens settings GUI)
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
| `show_components` | bool | Decomposition row from bundled data; no rebuild needed. |

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

## Packaging `.ankiaddon`

Build from the repo root. Exclude `__pycache__`, `meta.json` (user-local), and OS junk. Zip contents must be **top-level files** (no wrapping folder):

```bash
VERSION=$(python3 -c "from chinese_char_relations.about_meta import ADDON_VERSION; print(ADDON_VERSION)")
OUT="chinese_char_relations-${VERSION}.ankiaddon"
rm -f "$OUT"
(
  cd chinese_char_relations
  zip -r "../$OUT" . \
    -x '*/__pycache__/*' '*.pyc' 'meta.json' '.DS_Store' '*/.DS_Store'
)
unzip -l "$OUT"   # sanity-check: __init__.py at archive root
```

`preview/`, `docs/`, and tests stay outside `chinese_char_relations/` so they are never included.

### GitHub Release

**Required after every version push to `main`.** Users install from the Release asset, not from source.

1. Bump `ADDON_VERSION` + changelog in `about_meta.py` when shipping a new version.
2. Commit, push to `main`.
3. From repo root (after `gh auth login` once):

   ```bash
   ./scripts/release-github.sh
   ```

   This builds `chinese_char_relations-${VERSION}.ankiaddon`, creates tag `v${VERSION}` if missing, uploads the asset, and sets release notes from the changelog.

Manual equivalent:

```bash
VERSION=$(python3 -c "from chinese_char_relations.about_meta import ADDON_VERSION; print(ADDON_VERSION)")
OUT="chinese_char_relations-${VERSION}.ankiaddon"
# build zip (see Packaging section above)
gh release create "v${VERSION}" "$OUT" --title "v${VERSION}" --notes-file -
```

If the release already exists: `gh release upload "v${VERSION}" "$OUT" --clobber`

4. README install link uses `/releases/latest` (no edit needed per version).

### Publishing to AnkiWeb

**Live listing:** [Chinese Character Relations](https://ankiweb.net/shared/info/1076075855) · Get Add-ons code **`1076075855`**

1. Build the same `.ankiaddon` as above.
2. Upload at https://ankiweb.net/shared/addons/ (or update an existing branch).
3. AnkiWeb installs into a **numeric** folder under `addons21/`; `manifest.json` `package` matters mainly for offline `.ankiaddon` installs.
4. `URL_ANKIWEB` in `about_meta.py` points at the listing so the About tab shows **AnkiWeb page** and **Rate**. Mirror links in `preview/config-preview.html`.

Update the AnkiWeb description when behavior changes. Match the AnkiWeb listing version string to `ADDON_VERSION`.

### AnkiWeb description images

Screenshots live in [`docs/media/`](media/). After they are on `main`, paste HTML like this into the AnkiWeb listing description (same files as the README):

```html
<p><b>Dark mode</b> · <b>Light mode</b></p>
<img src="https://raw.githubusercontent.com/sageozzeus/Chinese-Character-Relations/main/docs/media/preview-dark.png" width="48%" />
<img src="https://raw.githubusercontent.com/sageozzeus/Chinese-Character-Relations/main/docs/media/preview-light.png" width="48%" />
<p><b>Settings — General</b> · <b>Settings — Appearance</b></p>
<img src="https://raw.githubusercontent.com/sageozzeus/Chinese-Character-Relations/main/docs/media/general-tab.png" width="48%" />
<img src="https://raw.githubusercontent.com/sageozzeus/Chinese-Character-Relations/main/docs/media/appearance-tab.png" width="48%" />
```

## Automated tests (no Anki)

CJK helpers are covered by unittest (does not need Anki/`aqt`):

```bash
cd /Users/urfan/Desktop/apps-websites/hanzi-relatives
python3 -m unittest tests.test_cjk tests.test_hanzi_ids tests.test_hanzi_data -v
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
