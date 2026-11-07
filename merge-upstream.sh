#!/usr/bin/env bash
# Usage: ./merge-upstream.sh pstack|mattpocock, right after that source's update script.
# The update script overwrites its skills with raw upstream. This three-way merges each
# overwritten file with HEAD's copy, so local edits (the Claude Code port, or my own
# changes to Matt's skills) survive wherever upstream didn't touch the same lines.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
case "${1:-}" in
  pstack) URL=https://github.com/cursor/plugins.git SHA_FILE=PSTACK_UPSTREAM ;;
  mattpocock) URL=https://github.com/mattpocock/skills.git SHA_FILE=MATTPOCOCK_UPSTREAM ;;
  *) echo "usage: $0 pstack|mattpocock" >&2; exit 2 ;;
esac
SOURCE="$1"
OLD="$(git show "HEAD:$SHA_FILE")"
NEW="$(cat "$SHA_FILE")"
if [ "$OLD" = "$NEW" ]; then
  git restore --source=HEAD --staged --worktree -- skills
  git clean -fdq -- skills
  rm -rf agents-upstream
  echo "Already at $SOURCE@${NEW:0:7}. Restored skills/ from HEAD. Nothing to merge."
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git -C "$TMP" init --quiet
git -C "$TMP" remote add origin "$URL"
git -C "$TMP" fetch --quiet --depth 1 --filter=blob:none origin "$OLD" "$NEW"

plugin_skills() {
  git -C "$TMP" show "$1:.claude-plugin/plugin.json" | python3 -I -c '
import json, os, sys
for path in json.load(sys.stdin)["skills"]:
    print(os.path.basename(path.rstrip("/")) + "\t" + os.path.normpath(path))
'
}
if [ "$SOURCE" = mattpocock ]; then
  plugin_skills "$OLD" > "$TMP/old-skills"
  plugin_skills "$NEW" > "$TMP/new-skills"
fi

upstream_path() {
  local name="${1#skills/}" rest
  rest="${name#*/}"
  name="${name%%/*}"
  case "$SOURCE" in
    pstack)
      case "$name" in
        pstack-tdd|pstack-teach) name="${name#pstack-}" ;;
      esac
      echo "pstack/skills/$name/$rest"
      ;;
    mattpocock)
      local dir
      dir="$(awk -F'\t' -v n="$name" '$1 == n {print $2}' "$TMP/old-skills")"
      [ -n "$dir" ] && echo "$dir/$rest"
      ;;
  esac
}

clean=0 conflicted=() added=() removed=() dropped=()
while IFS=$'\t' read -r status path; do
  case "$status" in
    M)
      base="$TMP/base" ours="$TMP/ours"
      up="$(upstream_path "$path" || true)"
      if [ -z "$up" ] || ! git -C "$TMP" show "$OLD:$up" > "$base" 2>/dev/null; then
        conflicted+=("$path (not from $SOURCE before this update. Name collision? Compare by hand)")
        continue
      fi
      git show "HEAD:$path" > "$ours"
      if git merge-file -L local -L "upstream@${OLD:0:7}" -L "upstream@${NEW:0:7}" "$ours" "$base" "$path"; then
        clean=$((clean + 1))
      else
        conflicted+=("$path")
      fi
      cp "$ours" "$path"
      ;;
    D) removed+=("$path") ;;
  esac
done < <(git diff --name-status HEAD -- skills)
while IFS= read -r path; do added+=("$path"); done < <(git ls-files --others --exclude-standard -- skills)
if [ "$SOURCE" = mattpocock ]; then
  while IFS= read -r name; do dropped+=("skills/$name"); done < <(
    comm -23 <(cut -f1 "$TMP/old-skills" | sort) <(cut -f1 "$TMP/new-skills" | sort))
fi

echo "Merged $SOURCE ${OLD:0:7}..${NEW:0:7}. $clean file(s) merged cleanly."
[ ${#conflicted[@]} -eq 0 ] || printf 'CONFLICT  %s\n' "${conflicted[@]}"
[ ${#added[@]} -eq 0 ] || printf 'NEW       %s\n' "${added[@]}"
[ ${#removed[@]} -eq 0 ] || printf 'REMOVED   %s\n' "${removed[@]}"
[ ${#dropped[@]} -eq 0 ] || printf 'DROPPED   %s (upstream no longer publishes it; delete by hand if unwanted)\n' "${dropped[@]}"
if [ "$SOURCE" = pstack ]; then
  agents="$(git -C "$TMP" diff --stat "$OLD" "$NEW" -- pstack/agents)"
  [ -z "$agents" ] || printf 'AGENTS changed upstream. Port into agents/ by hand:\n%s\n' "$agents"
fi
