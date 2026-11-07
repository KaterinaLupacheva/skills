#!/usr/bin/env bash
# Fails on Cursor-isms that PORTING.md maps away. Every pattern has zero hits on a
# fully ported tree, so any hit is a leftover from the last sync.
set -uo pipefail

ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$ROOT"
fail=0

patterns=(
  '~/\.cursor|\.cursor/(skills|rules|plugins|projects)'
  'pstack-models\.mdc'
  'generalPurpose'
  'readonly: (true|false)'
  'environment: "(cloud|local)"|cloud_base_branch'
  '\bAskQuestion\b'
  'subagent_type: "Comment Sicko"'
  'gpt-5\.|grok-4|claude-opus-[0-9-]+-(max|xhigh|high|medium|low)|claude-fable-'
  '/add-plugin|api2\.cursor\.sh'
  '^\| .*make-bot-ui'
  '^(<<<<<<<|>>>>>>>) '
  'fast or standard speed|Cursor cloud agent|VM dies'
  '/visualize'
  'Project (tracker|store)|Fork when new work'
  'runs `/deslop`|`deslop` skill|\(`/deslop`\)'
)
for p in "${patterns[@]}"; do
  if grep -rnE --exclude-dir=synced -- "$p" skills agents; then
    fail=1
  fi
done

for f in skills/*/SKILL.md; do
  dir="$(basename "$(dirname "$f")")"
  front="$(awk 'NR==1 && /^---$/ {on=1; next} on && /^---$/ {exit} on' "$f")"
  name="$(sed -n 's/^name: *//p' <<< "$front")"
  [ "$name" = "$dir" ] || { echo "$f: name '$name' does not match directory '$dir'"; fail=1; }
  if grep -nE '^(mode|icon|color|reminder|paths):' <<< "$front"; then
    echo "$f: Cursor-only frontmatter key"; fail=1
  fi
done

for f in skills/poteto-mode/SKILL.md skills/poteto-mode/playbooks/opening-a-pr.md agents/poteto-agent.md; do
  grep -qiE 'no commits, no PRs|Do not commit, push, or open a PR' "$f" \
    || { echo "$f: lost the local no-commits rule, re-apply it per PORTING.md"; fail=1; }
done

[ ! -e skills/make-bot-ui ] || { echo "skills/make-bot-ui: not portable, delete it"; fail=1; }

[ $fail -eq 0 ] && echo "Port check passed."
exit $fail
