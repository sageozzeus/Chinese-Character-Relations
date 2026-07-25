# -*- coding: utf-8 -*-
"""HTML/CSS for the Related panel injected into the reviewer."""

from __future__ import annotations

from html import escape
from typing import Any, Optional

from .defaults import merge_ui
from .indexer import RelatedEntry

# Structural CSS — colors/sizes come from CSS variables set per render.
# Keep structural rules in sync with preview/preview.html where practical.
PANEL_CSS = """
.char-relations {
  margin: 1.25em auto 0;
  max-width: var(--cr-max-width, 100%);
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--cr-gap, 0.75em);
  text-align: left;
  font-size: 0.92em;
  line-height: 1.35;
  color: inherit;
  box-sizing: border-box;
  padding: 0.75em 0.9em 0.85em;
  border: 1px solid var(--cr-border, #b0b0b0);
  border-radius: var(--cr-radius, 12px);
  background: var(--cr-bg, #e4ecf6);
  box-shadow: var(--cr-shadow, 0 3px 8px rgba(40, 35, 30, 0.07));
}
.char-relations-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5em;
  margin-bottom: 0.4em;
}
.char-relations-heading .char-relations-char {
  margin-bottom: 0;
  line-height: 1;
}
.char-relations-title {
  font-weight: 700;
  font-size: 0.9em;
  margin: 0;
  line-height: 1;
  flex: 0 0 auto;
  color: var(--cr-title, #1a3a6b);
}
.char-relations-group {
  box-sizing: border-box;
}
.char-relations-char {
  font-size: var(--cr-char-size, 1.05em);
  font-weight: 400;
  margin-bottom: 0.4em;
  opacity: 0.9;
}
.char-relations-scroll {
  position: relative;
  margin: 0;
}
.char-relations-items {
  display: flex;
  flex-wrap: nowrap;
  gap: 0.55em 0.95em;
  align-items: flex-end;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 0.1em 0;
  scroll-behavior: smooth;
}
.char-relations-items::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
.char-relations-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 0.08em;
  white-space: nowrap;
  flex: 0 0 auto;
  color: inherit;
  cursor: pointer;
}
.char-relations-item:hover .char-relations-word {
  text-decoration: underline;
  text-underline-offset: 0.12em;
}
.char-relations-pinyin {
  font-size: var(--cr-pinyin-size, 0.62em);
  font-weight: 400;
  opacity: 0.65;
  line-height: 1.15;
}
.char-relations-word {
  font-weight: 400;
  font-size: var(--cr-word-size, 0.82em);
  line-height: 1.2;
}
.char-relations-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.35em;
  height: 1.35em;
  padding: 0;
  margin: 0;
  border: 1px solid var(--cr-border, #b0b0b0);
  border-radius: 999px;
  background: var(--cr-bg, #e4ecf6);
  color: inherit;
  font-size: 0.95em;
  line-height: 0;
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease;
  box-shadow: var(--cr-shadow, 0 2px 6px rgba(40, 35, 30, 0.08));
  -webkit-appearance: none;
  appearance: none;
}
.char-relations-arrow::before {
  content: "";
  display: block;
  width: 0.36em;
  height: 0.36em;
  box-sizing: border-box;
  border: solid currentColor;
  border-width: 0 0 0.13em 0.13em;
}
.char-relations-arrow-left::before {
  transform: rotate(45deg);
}
.char-relations-arrow-right::before {
  border-width: 0.13em 0.13em 0 0;
  transform: rotate(45deg);
}
.char-relations-arrow-left { left: 0; }
.char-relations-arrow-right { right: 0; }
.char-relations-group:hover .char-relations-scroll.is-scrollable .char-relations-arrow {
  opacity: 0.85;
  pointer-events: auto;
}
.char-relations-group:hover .char-relations-scroll.is-scrollable .char-relations-arrow:hover {
  opacity: 1;
}
.char-relations-item.is-mature,
.char-relations-item.is-mature .char-relations-pinyin,
.char-relations-item.is-mature .char-relations-word {
  color: var(--cr-mature, #2e7d32);
}
.char-relations-item.is-mature .char-relations-pinyin {
  opacity: 0.85;
}
.char-relations-item.is-suspended,
.char-relations-item.is-suspended .char-relations-pinyin,
.char-relations-item.is-suspended .char-relations-word {
  color: var(--cr-suspended, #c62828);
}
.char-relations-item.is-suspended .char-relations-pinyin {
  opacity: 0.85;
}

.nightMode .char-relations,
.night-mode .char-relations {
  border-color: var(--cr-border-dark, #5a5a5a);
  background: var(--cr-bg-dark, #2a303a);
  box-shadow: var(--cr-shadow-dark, 0 4px 10px rgba(0, 0, 0, 0.28));
}
.nightMode .char-relations-title,
.night-mode .char-relations-title {
  color: var(--cr-title-dark, #b8dcff);
}
.nightMode .char-relations-char,
.night-mode .char-relations-char {
  opacity: 0.88;
}
.nightMode .char-relations-pinyin,
.night-mode .char-relations-pinyin {
  opacity: 0.65;
}
.nightMode .char-relations-arrow,
.night-mode .char-relations-arrow {
  border-color: var(--cr-border-dark, #5a5a5a);
  background: var(--cr-bg-dark, #2a303a);
  color: #e8e8e8;
  box-shadow: var(--cr-shadow-dark, 0 2px 8px rgba(0, 0, 0, 0.3));
}
.nightMode .char-relations-item.is-mature,
.nightMode .char-relations-item.is-mature .char-relations-pinyin,
.nightMode .char-relations-item.is-mature .char-relations-word,
.night-mode .char-relations-item.is-mature,
.night-mode .char-relations-item.is-mature .char-relations-pinyin,
.night-mode .char-relations-item.is-mature .char-relations-word {
  color: var(--cr-mature-dark, #81c784);
}
.nightMode .char-relations-item.is-suspended,
.nightMode .char-relations-item.is-suspended .char-relations-pinyin,
.nightMode .char-relations-item.is-suspended .char-relations-word,
.night-mode .char-relations-item.is-suspended,
.night-mode .char-relations-item.is-suspended .char-relations-pinyin,
.night-mode .char-relations-item.is-suspended .char-relations-word {
  color: var(--cr-suspended-dark, #ef9a9a);
}
"""

PANEL_JS = """
(function () {
  function refresh(wrap) {
    var track = wrap.querySelector(".char-relations-items");
    if (!track) return;
    var can = track.scrollWidth > track.clientWidth + 2;
    wrap.classList.toggle("is-scrollable", can);
  }
  function bindScroll(wrap) {
    if (wrap.getAttribute("data-cr-bound") === "1") {
      refresh(wrap);
      return;
    }
    wrap.setAttribute("data-cr-bound", "1");
    var track = wrap.querySelector(".char-relations-items");
    var left = wrap.querySelector(".char-relations-arrow-left");
    var right = wrap.querySelector(".char-relations-arrow-right");
    if (!track || !left || !right) return;
    left.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      track.scrollBy({ left: -160, behavior: "smooth" });
    });
    right.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      track.scrollBy({ left: 160, behavior: "smooth" });
    });
    track.addEventListener("scroll", function () { refresh(wrap); });
    if (window.ResizeObserver) {
      new ResizeObserver(function () { refresh(wrap); }).observe(track);
    }
    refresh(wrap);
  }
  function bindClicks() {
    document.querySelectorAll(".char-relations-item[data-nid]").forEach(function (el) {
      if (el.getAttribute("data-cr-click") === "1") return;
      el.setAttribute("data-cr-click", "1");
      el.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var nid = el.getAttribute("data-nid");
        if (!nid) return;
        if (typeof pycmd === "function") {
          pycmd("char_relations_browse:" + nid);
        }
      });
    });
  }
  document.querySelectorAll(".char-relations-scroll").forEach(bindScroll);
  bindClicks();
})();
"""


def _item_class(entry: RelatedEntry) -> str:
    if entry.suspended:
        return "char-relations-item is-suspended"
    if entry.mature:
        return "char-relations-item is-mature"
    return "char-relations-item"


def _css_var_block(ui: dict[str, Any]) -> str:
    """Inline style attribute setting CSS variables from ui config."""
    shadow_on = bool(ui.get("show_shadow", True))
    shadow = "0 3px 8px rgba(40, 35, 30, 0.07)" if shadow_on else "none"
    shadow_dark = "0 4px 10px rgba(0, 0, 0, 0.28)" if shadow_on else "none"
    pairs = {
        "--cr-max-width": str(ui.get("max_width") or "100%"),
        "--cr-gap": f"{float(ui.get('gap_em', 0.65))}em",
        "--cr-radius": f"{int(ui.get('border_radius_px', 12))}px",
        "--cr-char-size": f"{float(ui.get('char_size_em', 1.05))}em",
        "--cr-word-size": f"{float(ui.get('word_size_em', 0.82))}em",
        "--cr-pinyin-size": f"{float(ui.get('pinyin_size_em', 0.62))}em",
        "--cr-bg": str(ui.get("bg_light") or "#e4ecf6"),
        "--cr-bg-dark": str(ui.get("bg_dark") or "#2a303a"),
        "--cr-border": str(ui.get("border_light") or "#b0b0b0"),
        "--cr-border-dark": str(ui.get("border_dark") or "#5a5a5a"),
        "--cr-mature": str(ui.get("mature_light") or "#2e7d32"),
        "--cr-mature-dark": str(ui.get("mature_dark") or "#81c784"),
        "--cr-suspended": str(ui.get("suspended_light") or "#c62828"),
        "--cr-suspended-dark": str(ui.get("suspended_dark") or "#ef9a9a"),
        "--cr-shadow": shadow,
        "--cr-shadow-dark": shadow_dark,
    }
    return "; ".join(f"{k}: {escape(v, quote=True)}" for k, v in pairs.items())


def _safe_custom_css(css: str) -> str:
    """Prevent breaking out of the style tag."""
    return (css or "").replace("</", "<\\/")


def render_panel(
    groups: list[tuple[str, list[RelatedEntry]]],
    ui: Optional[dict[str, Any]] = None,
) -> str:
    """
    Build the Related panel HTML, or "" if there is nothing to show.

    *ui* comes from config["ui"] (Appearance tab). Defaults applied if omitted.
    """
    if not groups:
        return ""

    ui = merge_ui(ui)
    custom = _safe_custom_css(str(ui.get("custom_css") or "")).strip()
    custom_block = f"<style id=\"char-relations-custom\">{custom}</style>" if custom else ""

    parts: list[str] = [
        f"<style id=\"char-relations-style\">{PANEL_CSS}</style>",
        custom_block,
        f'<div class="char-relations" id="char-relations-panel" style="{_css_var_block(ui)}">',
    ]

    for i, (ch, entries) in enumerate(groups):
        parts.append('<div class="char-relations-group">')
        if i == 0:
            parts.append('<div class="char-relations-heading">')
            parts.append(f'<div class="char-relations-char">{escape(ch)}</div>')
            parts.append('<div class="char-relations-title">Relatives</div>')
            parts.append("</div>")
        else:
            parts.append(f'<div class="char-relations-char">{escape(ch)}</div>')
        parts.append('<div class="char-relations-scroll">')
        parts.append(
            '<button type="button" class="char-relations-arrow char-relations-arrow-left" '
            'aria-label="Scroll left"></button>'
        )
        parts.append('<div class="char-relations-items">')
        for entry in entries:
            word = escape(entry.word)
            pinyin = escape(entry.pinyin) if entry.pinyin else ""
            nid = int(entry.note_id)
            parts.append(
                f'<span class="{_item_class(entry)}" data-nid="{nid}" '
                f'role="button" title="Open in Browser" tabindex="0">'
            )
            if pinyin:
                parts.append(f'<span class="char-relations-pinyin">{pinyin}</span>')
            parts.append(f'<span class="char-relations-word">{word}</span>')
            parts.append("</span>")
        parts.append("</div>")
        parts.append(
            '<button type="button" class="char-relations-arrow char-relations-arrow-right" '
            'aria-label="Scroll right"></button>'
        )
        parts.append("</div>")
        parts.append("</div>")

    parts.append("</div>")
    parts.append(f"<script>{PANEL_JS}</script>")
    return "".join(parts)
