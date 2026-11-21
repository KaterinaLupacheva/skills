#!/usr/bin/env bash
# Print the prompt for the next step of a step plan. No model tokens.
#
#   next-step                 every plan under ./docs/plans with its next step
#   next-step <plan-dir>      the prompt for that plan's next step
#
# The next step is the first NN-*.md file, in number order, whose README row
# status is not `done`. With no README row, it is the first file with an
# unchecked box.
set -euo pipefail

status_of() {
  local readme=$1 file=$2
  [ -f "$readme" ] || return 0
  awk -F'|' -v f="$file" '
    function trim(s) { gsub(/^ +| +$/, "", s); return s }
    !col { for (i = 1; i <= NF; i++) if (trim($i) == "Status") col = i; next }
    index($0, "(" f ")") { print trim($col); exit }
  ' "$readme"
}

next_in() {
  local dir=${1%/} file status
  for path in "$dir"/[0-9][0-9]-*.md; do
    [ -f "$path" ] || continue
    file=$(basename "$path")
    status=$(status_of "$dir/README.md" "$file")
    if [ -n "$status" ]; then
      [ "$status" = done ] && continue
    elif ! grep -q -- '- \[ \]' "$path"; then
      continue
    fi
    printf '%s\t%s\n' "$file" "${status:-open boxes}"
    return 0
  done
  return 1
}

if [ $# -eq 0 ]; then
  [ -d docs/plans ] || { echo "No docs/plans here. Pass a plan folder." >&2; exit 1; }
  for dir in docs/plans/*/; do
    if hit=$(next_in "$dir"); then
      printf '%-40s %s (%s)\n' "${dir%/}" "${hit%%$'\t'*}" "${hit#*$'\t'}"
    fi
  done
  exit 0
fi

dir=${1%/}
hit=$(next_in "$dir") || { echo "All steps in $dir are done."; exit 0; }
file=${hit%%$'\t'*}
status=${hit#*$'\t'}
[ "$status" = blocked ] && echo "Note: $file is blocked. Check Blockers in $dir/README.md." >&2
if [ -f "$dir/README.md" ]; then
  echo "Implement $dir/$file. Read $dir/README.md first."
else
  echo "Implement $dir/$file."
fi
