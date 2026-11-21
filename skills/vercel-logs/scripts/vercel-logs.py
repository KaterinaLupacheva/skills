#!/usr/bin/env python3
"""Compact Vercel runtime logs. Wraps `vercel logs --json` and prints one short line per log
or, by default, one line per distinct message with a count.

  vercel-logs.py [--lines] [--grep REGEX] [--width N] [--max N] [-- any `vercel logs` options]

Defaults passed to `vercel logs`: --since 1h --limit 500. Override them after `--`, for example
  vercel-logs.py -- --environment production --level error --since 30m
  vercel-logs.py --grep "credentials" -- --since 2h --project store-connect
Run it from the linked project folder, or pass --project after `--`.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime

parser = argparse.ArgumentParser(usage=__doc__)
parser.add_argument("--lines", action="store_true", help="one line per log, newest first, instead of grouped counts")
parser.add_argument("--grep", help="keep only logs whose path or message matches this regex (case-insensitive)")
parser.add_argument("--width", type=int, default=220, help="max characters of message per line")
parser.add_argument("--max", type=int, default=40, help="max output lines")
args, rest = parser.parse_known_args()
rest = [a for a in rest if a != "--"]

defaults = []
if not any(a == "--since" or a.startswith("--since=") for a in rest):
    defaults += ["--since", "1h"]
if not any(a in ("-n", "--limit") or a.startswith("--limit=") for a in rest):
    defaults += ["--limit", "500"]
cmd = ["vercel", "logs", "--json", "--no-color", *defaults, *rest]
proc = subprocess.run(cmd, capture_output=True, text=True)
if proc.returncode != 0 and not proc.stdout.strip():
    sys.stderr.write(proc.stderr[-2000:])
    sys.exit(proc.returncode)

pattern = re.compile(args.grep, re.I) if args.grep else None
records = []
for line in proc.stdout.splitlines():
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        r = json.loads(line)
    except json.JSONDecodeError:
        continue
    message = " ".join((r.get("message") or "").split())
    status = r.get("responseStatusCode") or 0
    if not message and status < 400:
        continue
    path = r.get("requestPath") or ""
    if pattern and not (pattern.search(message) or pattern.search(path)):
        continue
    records.append((r.get("timestamp") or 0, r.get("level") or "", status, r.get("requestMethod") or "", path, message))


def clock(ms):
    return datetime.fromtimestamp(ms / 1000).strftime("%m-%d %H:%M:%S")


def clip(text):
    return text if len(text) <= args.width else text[: args.width - 1] + "…"


def signature(message):
    message = re.sub(r"[0-9a-f]{8}-[0-9a-f-]{27,}[\w-]*", "<id>", message)
    message = re.sub(r"\b\d[\d.:,-]*\b", "<n>", message)
    return message[:160]


print(f"{len(records)} logs kept from `{' '.join(cmd[2:])}`" + (f", grep /{args.grep}/" if args.grep else ""))
if not records:
    sys.exit(0)

if args.lines:
    out = [f"{clock(t)} {lvl:5} {st or '-':>3} {m} {p} | {clip(msg)}" for t, lvl, st, m, p, msg in sorted(records, reverse=True)]
else:
    groups = {}
    for t, lvl, st, m, p, msg in records:
        key = (lvl, st, p, signature(msg))
        g = groups.setdefault(key, {"n": 0, "first": t, "last": t, "msg": msg, "method": m})
        g["n"] += 1
        g["first"], g["last"] = min(g["first"], t), max(g["last"], t)
    rank = {"fatal": 0, "error": 1, "warning": 2}
    ordered = sorted(groups.items(), key=lambda kv: (rank.get(kv[0][0], 3), -kv[1]["n"]))
    out = [
        f"{g['n']:>4}x {lvl:5} {st or '-':>3} {g['method']} {p} [{clock(g['first'])} → {clock(g['last'])}] | {clip(g['msg'])}"
        for (lvl, st, p, _), g in ordered
    ]
for line in out[: args.max]:
    print(line)
if len(out) > args.max:
    print(f"… {len(out) - args.max} more lines. Narrow with --grep, --level or --since, or raise --max.")
