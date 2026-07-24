# -*- coding: utf-8 -*-
"""HTML/CSS for the Related panel injected into the reviewer."""

from __future__ import annotations

from html import escape

from .indexer import RelatedEntry

# Keep in sync with preview/preview.html
PANEL_CSS = """
.char-relations {
  margin: 1.25em auto 0;
  max-width: 36em;
  display: flex;
  flex-direction: column;
  gap: 0.65em;
  text-align: left;
  font-size: 0.92em;
  line-height: 1.35;
  color: inherit;
  box-sizing: border-box;
}
.char-relations-group {
  padding: 0.75em 0.9em 0.85em;
  border: 1px solid rgba(120, 120, 120, 0.28);
  border-radius: 12px;
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.78) 0%,
      rgba(255, 255, 255, 0.52) 100%
    );
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.7) inset,
    0 3px 8px rgba(40, 35, 30, 0.07);
  box-sizing: border-box;
}
.char-relations-char {
  font-size: 1.05em;
  font-weight: 400;
  margin-bottom: 0.4em;
  opacity: 0.9;
}
.char-relations-scroll {
  position: relative;
  margin: 0 -0.15em;
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
  padding: 0.1em 1.15em;
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
  font-size: 0.62em;
  font-weight: 400;
  opacity: 0.65;
  line-height: 1.15;
}
.char-relations-word {
  font-weight: 400;
  font-size: 0.82em;
  line-height: 1.2;
}
.char-relations-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 1.35em;
  height: 1.35em;
  padding: 0;
  margin: 0;
  border: 1px solid rgba(120, 120, 120, 0.28);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: inherit;
  font-size: 0.95em;
  font-weight: 400;
  line-height: 1;
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease;
  box-shadow: 0 2px 6px rgba(40, 35, 30, 0.08);
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
  color: #2e7d32;
}
.char-relations-item.is-mature .char-relations-pinyin {
  opacity: 0.85;
}
.char-relations-item.is-suspended,
.char-relations-item.is-suspended .char-relations-pinyin,
.char-relations-item.is-suspended .char-relations-word {
  color: #c62828;
}
.char-relations-item.is-suspended .char-relations-pinyin {
  opacity: 0.85;
}

.nightMode .char-relations-group,
.night-mode .char-relations-group {
  border: 1px solid rgba(255, 255, 255, 0.18);
  background:
    linear-gradient(
      180deg,
      rgba(58, 60, 66, 0.95) 0%,
      rgba(40, 42, 48, 0.95) 100%
    );
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.07) inset,
    0 4px 10px rgba(0, 0, 0, 0.28);
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
  border-color: rgba(255, 255, 255, 0.18);
  background: rgba(48, 50, 56, 0.95);
  color: #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
.nightMode .char-relations-item.is-mature,
.nightMode .char-relations-item.is-mature .char-relations-pinyin,
.nightMode .char-relations-item.is-mature .char-relations-word,
.night-mode .char-relations-item.is-mature,
.night-mode .char-relations-item.is-mature .char-relations-pinyin,
.night-mode .char-relations-item.is-mature .char-relations-word {
  color: #81c784;
}
.nightMode .char-relations-item.is-suspended,
.nightMode .char-relations-item.is-suspended .char-relations-pinyin,
.nightMode .char-relations-item.is-suspended .char-relations-word,
.night-mode .char-relations-item.is-suspended,
.night-mode .char-relations-item.is-suspended .char-relations-pinyin,
.night-mode .char-relations-item.is-suspended .char-relations-word {
  color: #ef9a9a;
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


def render_panel(groups: list[tuple[str, list[RelatedEntry]]]) -> str:
    """
    Build the Related panel HTML, or "" if there is nothing to show.

    Each character group is its own bordered card with a single-row
    horizontal scroller (arrows on hover when overflow exists).
    Words are clickable and open the note in Browser via pycmd.
    """
    if not groups:
        return ""

    parts: list[str] = [
        f"<style>{PANEL_CSS}</style>",
        '<div class="char-relations" id="char-relations-panel">',
    ]

    for ch, entries in groups:
        parts.append('<div class="char-relations-group">')
        parts.append(f'<div class="char-relations-char">{escape(ch)}</div>')
        parts.append('<div class="char-relations-scroll">')
        parts.append(
            '<button type="button" class="char-relations-arrow char-relations-arrow-left" '
            'aria-label="Scroll left">‹</button>'
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
            'aria-label="Scroll right">›</button>'
        )
        parts.append("</div>")
        parts.append("</div>")

    parts.append("</div>")
    parts.append(f"<script>{PANEL_JS}</script>")
    return "".join(parts)
