# Chinese Character Relations — Config

Settings are edited in a **GUI dialog** (no JSON editing required):

- **Tools → Character Relations → Settings…**
- or **Tools → Add-ons → Chinese Character Relations → Config**

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

`config.json` only supplies defaults for first install. Advanced users can still find values in the add-on `meta.json`, but the GUI is the supported path.
