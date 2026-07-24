# -*- coding: utf-8 -*-
"""Reviewer hooks: append Related panel to the answer HTML."""

from __future__ import annotations

from typing import Any, Optional

from anki.cards import Card
from aqt import mw

from .cjk import strip_html
from .defaults import merge_config
from .indexer import FALLBACK_WORD_FIELDS, get_index, resolve_field
from .render import PANEL_JS, render_panel


def _package_name() -> str:
    return __name__.split(".")[0]


def _config() -> dict[str, Any]:
    return merge_config(mw.addonManager.getConfig(_package_name()))


def _field(config: dict[str, Any], key: str, default: str) -> str:
    fields = config.get("fields") or {}
    return (fields.get(key) or default).strip()


def _word_from_note(note: Any, config: dict[str, Any]) -> tuple[Optional[str], Optional[int]]:
    """Return (word, note_id) using the same field resolution as the indexer."""
    wanted = _field(config, "word", "Word")
    resolved = resolve_field(note, wanted, FALLBACK_WORD_FIELDS)
    if not resolved:
        return None, None
    word = strip_html(note[resolved])
    if not word:
        return None, None
    try:
        nid = int(note.id)
    except Exception:
        nid = None
    return word, nid


def panel_html_for_card(card: Card) -> str:
    """Build Related panel HTML for *card*, or "" if nothing to show."""
    idx = get_index()
    if not idx.note_count and not idx._index:
        return ""

    config = _config()
    try:
        note = card.note()
    except Exception:
        return ""

    word, note_id = _word_from_note(note, config)
    if not word:
        return ""

    groups = idx.related_for(word, config, note_id=note_id)
    return render_panel(groups, ui=config.get("ui"))


def on_card_will_show(html: str, card: Card, context: str) -> str:
    """
    Reliable injection: append panel HTML before Anki paints the answer.

    Prefer this over webview.eval — fade/DOM updates often wipe late eval inserts.
    """
    if context != "reviewAnswer":
        return html
    panel = panel_html_for_card(card)
    if not panel:
        return html
    return html + panel


def on_show_answer(card: Card) -> None:
    """Fallback inject if needed, then bind horizontal scroll arrows."""
    if mw.reviewer is None or mw.reviewer.web is None:
        return
    panel = panel_html_for_card(card)
    if panel:
        import json

        payload = json.dumps(panel)
        js = f"""
        (function() {{
          if (document.getElementById('char-relations-panel')) {{ return; }}
          var target = document.getElementById('qa') || document.body;
          var tmp = document.createElement('div');
          tmp.innerHTML = {payload};
          while (tmp.firstChild) {{
            var child = tmp.firstChild;
            if (child.nodeName === 'SCRIPT') {{
              tmp.removeChild(child);
              continue;
            }}
            if (child.nodeName === 'STYLE') {{ child.id = 'char-relations-style'; }}
            target.appendChild(child);
          }}
        }})();
        """
        mw.reviewer.web.eval(js)
    # Scripts inside card HTML are not always executed — bind via eval
    mw.reviewer.web.eval(PANEL_JS)


def on_show_question(card: Card) -> None:
    # card_will_show replaces #qa content; nothing required.
    # Clear any leftover fallback injection just in case.
    if mw.reviewer is None or mw.reviewer.web is None:
        return
    mw.reviewer.web.eval(
        """
        (function() {
          var el = document.getElementById('char-relations-panel');
          if (el) { el.remove(); }
          var st = document.getElementById('char-relations-style');
          if (st) { st.remove(); }
        })();
        """
    )
