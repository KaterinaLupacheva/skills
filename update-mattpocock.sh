#!/usr/bin/env bash
# Replace Matt Pocock's skills in skills/ with the latest from mattpocock/skills.
# Takes exactly the skills his Claude Code plugin publishes, flattened to skills/<name>.
# Other skills are untouched. Review with `git diff` before committing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git clone --quiet --depth 1 https://github.com/mattpocock/skills.git "$TMP/mp"

python3 -I -c '
import json, sys
for path in json.load(open(sys.argv[1]))["skills"]:
    print(path)
' "$TMP/mp/.claude-plugin/plugin.json" > "$TMP/list"

while IFS= read -r path; do
  src="$TMP/mp/$path"
  name="$(basename "$path")"
  [ -f "$src/SKILL.md" ] || { echo "error: $path has no SKILL.md" >&2; exit 1; }
  mkdir -p "$ROOT/skills/$name"
  rsync -a --delete --exclude .DS_Store "$src/" "$ROOT/skills/$name/"
done < "$TMP/list"

cp "$TMP/mp/LICENSE" "$ROOT/licenses/mattpocock-skills.txt"
git -C "$TMP/mp" rev-parse HEAD > "$ROOT/MATTPOCOCK_UPSTREAM"
echo "Updated Matt Pocock's skills to mattpocock/skills@$(cut -c1-7 "$ROOT/MATTPOCOCK_UPSTREAM") ($(wc -l < "$TMP/list" | tr -d ' ') skills)"
