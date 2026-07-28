# Chinese Character Relations — Config

Settings are edited in a **GUI dialog** (no JSON editing required):

- **Tools → Chinese Character Relations…**
- or **Tools → Add-ons → Chinese Character Relations → Config**

## General tab

| Setting | Default | Meaning |
| --- | --- | --- |
| Decks | All decks | Dropdown with checkboxes; empty list in storage = all decks |
| Word / Hanzi field | `Word` | Headword field on notes |
| Pinyin field | `Pinyin` | Reading (optional) |
| Max per character | `8` | Cap on related rows per character group |
| Include suspended | yes | Show notes whose cards are all suspended |
| Min word length | `2` | Minimum CJK length for related candidates |
| Show only on back | yes | Off = show relatives on front and back during review |
| Show character components | yes | Decomposition row (pinyin above each part; English on hover). Bundled data — **no rebuild** |
| Rebuild Index | button | Scans decks and refreshes the character → notes index |

### Components row (when enabled)

- Shown **above** each character’s related words for every CJK character in the reviewed word.
- Layout: head character → components, with pinyin on each; **Relatives** label on the first row only (top right).
- Meanings appear **only on hover** over a character or component (desktop).
- Turn off under **Show character components** if you only want deck relatives.

After changing decks or fields, rebuild when prompted (or use **Rebuild Index** on this tab).

## Appearance tab

Customize Related panel look. Applies on the next answer flip (no rebuild).

| Setting | Default | Notes |
| --- | --- | --- |
| Max width | `100%` | e.g. `100%`, `36em`, `650px` — match your card template |
| Corner radius | `12` px | |
| Gap between cards | `0.65` em | Label in UI: **Card gaps** |
| Type sizes | char / word / pinyin | Relative `em` sizes |
| Colors | light + dark | 4×2 grid; background, border, mature, suspended |
| Custom CSS | empty | Advanced overrides for `.char-relations*` |

## About tab

Read-only. Version, license, changelog, and links (GitHub Issues for bugs, GitHub repo, X, AnkiWeb page, Rate).

`config.json` supplies defaults for first install. User values live in `meta.json`.
