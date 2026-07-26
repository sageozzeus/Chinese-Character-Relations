#!/usr/bin/env bash
# Build .ankiaddon and create or update the matching GitHub Release.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VERSION=$(python3 -c "from chinese_char_relations.about_meta import ADDON_VERSION; print(ADDON_VERSION)")
OUT="chinese_char_relations-${VERSION}.ankiaddon"

echo "Building ${OUT}…"
rm -f "$OUT"
(
  cd chinese_char_relations
  zip -r "../$OUT" . \
    -x '*/__pycache__/*' '__pycache__/*' '*.pyc' 'meta.json' '.DS_Store' '*/.DS_Store'
)

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  TAG="v${VERSION}"
  NOTES=$(python3 -c "
from chinese_char_relations.about_meta import ADDON_VERSION, CHANGELOG
ver = ADDON_VERSION
lines = [f'## Chinese Character Relations {ver}', '']
for v, bullets in CHANGELOG:
    if v == ver:
        for b in bullets:
            lines.append(f'- {b}')
        break
print(chr(10).join(lines))
")
  if gh release view "$TAG" >/dev/null 2>&1; then
    gh release upload "$TAG" "$OUT" --clobber
    gh release edit "$TAG" --notes "$NOTES"
  else
    gh release create "$TAG" "$OUT" --title "$TAG" --notes "$NOTES"
  fi
  gh release view "$TAG" --json url -q .url
else
  python3 scripts/publish_github_release.py
fi
