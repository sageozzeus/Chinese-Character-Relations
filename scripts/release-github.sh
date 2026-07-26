#!/usr/bin/env bash
# Build .ankiaddon and create or update the matching GitHub Release.
# Requires: gh auth login (once per machine)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: brew install gh" >&2
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "Run: gh auth login" >&2
  exit 1
fi

VERSION=$(python3 -c "from chinese_char_relations.about_meta import ADDON_VERSION; print(ADDON_VERSION)")
TAG="v${VERSION}"
OUT="chinese_char_relations-${VERSION}.ankiaddon"

echo "Building ${OUT}…"
rm -f "$OUT"
(
  cd chinese_char_relations
  zip -r "../$OUT" . \
    -x '*/__pycache__/*' '__pycache__/*' '*.pyc' 'meta.json' '.DS_Store' '*/.DS_Store'
)

NOTES=$(python3 << PY
from chinese_char_relations.about_meta import ADDON_VERSION, CHANGELOG
ver = ADDON_VERSION
lines = [f"## Chinese Character Relations {ver}", ""]
for v, bullets in CHANGELOG:
    if v == ver:
        for b in bullets:
            lines.append(f"- {b}")
        break
else:
    lines.append(f"Release {ver}.")
print("\\n".join(lines))
PY
)

if gh release view "$TAG" >/dev/null 2>&1; then
  echo "Release ${TAG} exists — uploading asset…"
  gh release upload "$TAG" "$OUT" --clobber
  gh release edit "$TAG" --notes "$NOTES"
else
  echo "Creating release ${TAG}…"
  gh release create "$TAG" "$OUT" --title "$TAG" --notes "$NOTES"
fi

echo "Done: $(gh release view "$TAG" --json url -q .url)"
