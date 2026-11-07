#!/usr/bin/env bash
# Replace pstack skills in skills/ with the latest from cursor/plugins.
# Your own skills are untouched. Review with `git diff` before committing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git clone --quiet --depth 1 --filter=blob:none --sparse \
  https://github.com/cursor/plugins.git "$TMP/plugins"
git -C "$TMP/plugins" sparse-checkout set pstack

for dir in "$TMP/plugins/pstack/skills"/*/; do
  [ "$(basename "$dir")" = make-bot-ui ] && continue
  name="$(basename "$dir")"
  # Matt Pocock's skills own these names here. Port references per PORTING.md.
  case "$name" in
    tdd|teach) name="pstack-$name" ;;
  esac
  mkdir -p "$ROOT/skills/$name"
  rsync -a --delete --exclude .DS_Store "$dir" "$ROOT/skills/$name/"
done

# Upstream's Cursor agents land outside agents/, which both workspaces load.
# Port changes from here into agents/ by hand.
mkdir -p "$ROOT/agents-upstream"
rsync -a --delete --exclude .DS_Store "$TMP/plugins/pstack/agents/" "$ROOT/agents-upstream/"

cp "$TMP/plugins/pstack/LICENSE" "$ROOT/licenses/pstack.txt"
git -C "$TMP/plugins" rev-parse HEAD > "$ROOT/PSTACK_UPSTREAM"
echo "Updated pstack to cursor/plugins@$(cut -c1-7 "$ROOT/PSTACK_UPSTREAM")"
echo "Upstream targets Cursor. Re-apply the Claude Code port before committing: see PORTING.md"
