# Chinese Character Relations

Anki desktop add-on that shows **related words from your own deck** that share Chinese characters with the card you’re reviewing.

Example: reviewing **好** → under the answer you see 好像, 好的, 好听…  
Reviewing **好像** → groups by 好 and 像 (the current word is excluded).

Works offline. Uses only your collection — no external dictionary, no AnkiConnect.

## Screenshots

<table>
  <tr>
    <td align="center" width="50%">
      <p><strong>Dark mode</strong></p>
      <img src="docs/media/preview-dark.png" alt="Related words on the answer side (dark mode)" />
    </td>
    <td align="center" width="50%">
      <p><strong>Light mode</strong></p>
      <img src="docs/media/preview-light.png" alt="Related words on the answer side (light mode)" />
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <p><strong>Settings — General</strong></p>
      <img src="docs/media/general-tab.png" alt="General settings tab" />
    </td>
    <td align="center" width="50%">
      <p><strong>Settings — Appearance</strong></p>
      <img src="docs/media/appearance-tab.png" alt="Appearance settings tab" />
    </td>
  </tr>
</table>

## Requirements

- Anki Desktop **23.10+** (Qt6 preferred)
- macOS, Windows, or Linux

## Install

**From AnkiWeb** (when the listing is live): search for *Chinese Character Relations* in **Tools → Add-ons → Get Add-ons…**, or open the listing from the About tab after install.

**From this repo:**

1. Download or clone the repository.
2. Copy the `chinese_char_relations` folder into your Anki add-ons folder:

   - **macOS:** `~/Library/Application Support/Anki2/addons21/`
   - **Windows:** `%APPDATA%\Anki2\addons21\`
   - **Linux:** `~/.local/share/Anki2/addons21/`

3. Restart Anki.
4. Open **Tools → Character Relations…**
5. On the **General** tab, set your Word / Hanzi (and optional Pinyin) fields, then click **Rebuild Index**.

## Settings

**Tools → Character Relations…** (or **Tools → Add-ons → Config**):

| Tab | What it’s for |
| --- | --- |
| **General** | Decks, field names, display limits, **Rebuild Index** |
| **Appearance** | Panel width, type sizes, colors, optional custom CSS |
| **About** | Version, changelog, bug reports, links |

After changing decks or fields, rebuild when prompted (or use **Rebuild Index**). Appearance changes apply on the next answer flip — no rebuild needed.

Defaults assume a `Word` and `Pinyin` field. If your deck uses `Hanzi` / `Expression` / etc., set those names on the General tab.

## Tips

- Click a related word to open that note in the Browser.
- If nothing related appears, check field names and rebuild; rare characters with no other deck words simply show no panel.
- Suspended notes can be included or hidden on the General tab.

## Support

- **Bugs:** [GitHub Issues](https://github.com/sageozzeus/Chinese-Character-Relations/issues)
- **Updates / short questions:** [X @sageozzeus](https://x.com/sageozzeus)
- **Source:** [github.com/sageozzeus/Chinese-Character-Relations](https://github.com/sageozzeus/Chinese-Character-Relations)

Maintainer docs (dev setup, architecture, packaging): [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md) · QA checklist: [`docs/TESTING.md`](docs/TESTING.md)

## License

MIT — see [`LICENSE`](LICENSE).
