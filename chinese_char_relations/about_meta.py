# -*- coding: utf-8 -*-
"""Add-on identity, links, and changelog for the About settings tab.

Bump ADDON_VERSION and prepend a CHANGELOG entry whenever you ship.
After publishing on AnkiWeb, set URL_ANKIWEB to the listing URL
(e.g. https://ankiweb.net/shared/info/<id>) so AnkiWeb / Rate links appear.
"""

from __future__ import annotations

from typing import List, Tuple

ADDON_NAME = "Chinese Character Relations"
ADDON_VERSION = "0.2.1"
MIN_ANKI = "23.10+"
AUTHOR = "Ozzeus"
LICENSE = "MIT"

URL_GITHUB = "https://github.com/sageozzeus/Chinese-Character-Relations"
URL_ISSUES = URL_GITHUB + "/issues"
URL_X = "https://x.com/sageozzeus"
URL_ANKIWEB = "https://ankiweb.net/shared/info/1076075855"

# Newest first. Keep the latest entry to ~5 bullets for the About dialog.
CHANGELOG: List[Tuple[str, List[str]]] = [
    (
        "0.2.1",
        [
            "AnkiWeb listing link and Rate button on the About tab",
        ],
    ),
    (
        "0.2.0",
        [
            "Character decomposition row per hanzi (components + pinyin)",
            "English meanings on hover for the character and each component",
            "Shows all characters in a word even when only some have deck relatives",
            "Toggle components in General → Display options",
            "Bundled make-me-a-hanzi data (offline, ~900 KB)",
        ],
    ),
    (
        "0.1.0",
        [
            "Related words from your own deck by shared Chinese characters",
            "General and Appearance settings GUI (no JSON editing)",
            "Click a related word to open it in the Browser",
            "Light/dark panel colors and optional custom CSS",
            "Rebuild Index from Tools → Chinese Character Relations…",
        ],
    ),
]
