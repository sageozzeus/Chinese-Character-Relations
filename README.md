# Chinese Character Relations

Anki 2.1+ desktop add-on that shows **related words from your own deck** sharing Chinese characters with the card you’re reviewing — on the answer side.

Example: reviewing **好** → under the answer you see 好像, 好的, 好听…  
Reviewing **好像** → groups by 好 and 像 (current word excluded).

Works offline. Uses only `mw.col` (no AnkiConnect, no external dictionary for MVP).

## Requirements

- Anki Desktop **23.10+** (Qt6 preferred)
- macOS first (Linux/Windows paths differ only for the add-ons folder)

## Install (end users)

1. Copy the `chinese_char_relations` folder into:

   `~/Library/Application Support/Anki2/addons21/`

2. Restart Anki.
3. **Tools → Character Relations → Settings…** (or Add-ons → Config) — pick decks and field names from dropdowns. No JSON editing.
4. When prompted, rebuild the index (or use **Tools → Character Relations → Rebuild Index**).

## Development setup (symlink)

Do **not** copy the folder on every change. Symlink once:

```bash
./scripts/link-anki-addon.sh
# or:
ln -s "/Users/urfan/Desktop/apps-websites/hanzi-relatives/chinese_char_relations" \
  "$HOME/Library/Application Support/Anki2/addons21/chinese_char_relations"
```

Then: edit in this repo → quit & reopen Anki (**Cmd+Q**) → flip a card.

If a real folder already exists at that path, rename it before creating the symlink.

Maintainer deep-dive: [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md).

## UI preview (no Anki)

Open [`preview/preview.html`](preview/preview.html) in a browser (**Cmd+O**).

Edit the `.char-relations*` CSS there, then copy the same rules into `chinese_char_relations/render.py` (`PANEL_CSS`).

## Config

Use the GUI (**Tools → Character Relations → Settings…**). Defaults:

| Key | Default | Notes |
| --- | --- | --- |
| Decks | All decks | Or multi-select specific decks |
| Word / Hanzi | `Word` | Headword field |
| Pinyin | `Pinyin` | Optional |
| Meaning | `Meaning` | Optional |
| Max per character | `8` | Cap per character group |
| Include suspended | yes | Filter at lookup time |
| Min word length | `2` | Min CJK length for relatives |
| Answer side only | yes | MVP |

## Manual test checklist

- [ ] Single-char card shows multi-char relatives containing that char
- [ ] Multi-char card groups by each character
- [ ] Current headword is excluded from the list
- [ ] `include_suspended: false` hides fully inactive notes
- [ ] Wrong / missing field names → no crash (tooltip at most once per session)
- [ ] After adding a note, **Rebuild Index** makes it appear in Related
- [ ] Front of card has no Related panel; answer shows it when relations exist
- [ ] Empty relations → no empty box under the card

## Package for AnkiWeb

```bash
cd chinese_char_relations
rm -rf __pycache__ **/__pycache__
zip -r ../chinese_char_relations.ankiaddon *
```

Upload at https://ankiweb.net/shared/addons/ (zip must contain files at top level, not a wrapping folder).

## Docs

- [Maintenance & architecture](docs/MAINTENANCE.md) — how to change index, hooks, UI, publish
- [Manual test details](docs/TESTING.md)

## License

MIT (or your choice when publishing).
