# Chinese Character Relations — Config

Settings are edited in a **GUI dialog** (no JSON editing required):

- **Tools → Character Relations → Settings…**
- or **Tools → Add-ons → Chinese Character Relations → Config**

## General tab

| Setting | Default | Meaning |
| --- | --- | --- |
| Decks | All decks | Empty list in storage = all decks; otherwise only checked decks |
| Word / Hanzi field | `Word` | Headword field on notes |
| Pinyin field | `Pinyin` | Reading (optional) |
| Meaning field | `Meaning` | Gloss (optional) |
| Max per character | `8` | Cap on related rows per character group |
| Include suspended | yes | Show notes whose cards are all suspended |
| Min word length | `2` | Minimum CJK length for related candidates |
| Show on answer only | yes | Related panel only after flip (MVP) |

After changing decks or fields, rebuild when prompted (or **Tools → Character Relations → Rebuild Index**).

## Appearance tab

Customize Related panel look. Applies on the next answer flip (no rebuild).

| Setting | Default | Notes |
| --- | --- | --- |
| Max width | `100%` | e.g. `100%`, `36em`, `650px` — match your card template |
| Corner radius | `12` px | |
| Gap between cards | `0.65` em | Space between character groups |
| Type sizes | char / word / pinyin | Relative `em` sizes |
| Colors | light + dark | Background, border, mature (green), suspended (red) |
| Drop shadow | on | |
| Custom CSS | empty | Advanced overrides for `.char-relations*` |

`config.json` supplies defaults for first install. User values live in `meta.json`.
