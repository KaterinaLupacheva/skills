#!/usr/bin/env bash
# Replace the CLI tools clean-mode runs with the latest from unclebob/*.
# clean-mode's SKILL.md is my own rewrite of unclebob/ub-mode, so ub-mode
# changes are only reported for porting by hand.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$ROOT/skills/clean-mode/tools"
UPSTREAM="$TOOLS/UPSTREAM"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

old_ub="$(awk '$1 == "ub-mode" { print $2 }' "$UPSTREAM" 2>/dev/null || true)"
: > "$TMP/UPSTREAM"

for repo in crapper dryer mutator ub-mode; do
  git clone --quiet --depth 1 "https://github.com/unclebob/$repo.git" "$TMP/$repo"
  echo "$repo $(git -C "$TMP/$repo" rev-parse HEAD)" >> "$TMP/UPSTREAM"
  if [ "$repo" = ub-mode ]; then
    cp "$TMP/$repo/LICENSE" "$ROOT/skills/clean-mode/LICENSE-ub-mode"
    continue
  fi
  mkdir -p "$TOOLS/$repo"
  # Excluded paths survive --delete, so the installed virtualenv stays.
  rsync -a --delete --exclude .git --exclude .DS_Store --exclude .venv \
    --exclude '*.egg-info' "$TMP/$repo/" "$TOOLS/$repo/"
done

mv "$TMP/UPSTREAM" "$UPSTREAM"
cat "$UPSTREAM"

new_ub="$(awk '$1 == "ub-mode" { print $2 }' "$UPSTREAM")"
if [ -n "$old_ub" ] && [ "$old_ub" != "$new_ub" ]; then
  echo "ub-mode changed upstream. Port what applies into skills/clean-mode/SKILL.md:"
  echo "https://github.com/unclebob/ub-mode/compare/$old_ub...$new_ub"
fi
