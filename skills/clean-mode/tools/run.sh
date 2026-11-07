#!/bin/sh
# Usage: run.sh crapper|dryer|mutator [args...]
# The tools' own launchers build their virtualenv with whatever python3 comes
# first on PATH, which may be older than the 3.11 they need. Build it here with
# the newest Python found, then hand over to the launcher.
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
TOOL=$1
case "$TOOL" in
  crapper|dryer|mutator) shift ;;
  *) echo "usage: $0 crapper|dryer|mutator [args...]" >&2; exit 64 ;;
esac

VENV="$ROOT/$TOOL/.venv"
if [ ! -x "$VENV/bin/python" ]; then
  for PY in python3.14 python3.13 python3.12 python3.11 python3; do
    command -v "$PY" >/dev/null 2>&1 || continue
    "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 11))' || continue
    if "$PY" -m venv "$VENV" && "$VENV/bin/pip" install -q -e "$ROOT/$TOOL"; then
      break
    fi
    rm -rf "$VENV"
    exit 1
  done
  if [ ! -x "$VENV/bin/python" ]; then
    echo "$TOOL needs Python 3.11+. Install one with: brew install python@3.12" >&2
    exit 69
  fi
fi
exec "$ROOT/$TOOL/$TOOL" "$@"
