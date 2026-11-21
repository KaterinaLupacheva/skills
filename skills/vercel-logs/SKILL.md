---
name: vercel-logs
description: Read Vercel runtime logs as compact grouped lines. Use instead of the Vercel MCP log tools or raw `vercel logs` when checking a deploy, an error, or an endpoint's behavior.
---

# Vercel logs

Run [`scripts/vercel-logs.py`](scripts/vercel-logs.py) from the linked project folder. It calls `vercel logs --json` and prints one line per distinct message with a count, errors first, capped at 40 lines. Never call the Vercel MCP log tools or plain `vercel logs`: they return every request in full and flood the context.

```
python3 <skill-dir>/scripts/vercel-logs.py -- --environment production --level error --since 1h
python3 <skill-dir>/scripts/vercel-logs.py --grep "credentials|webhook" -- --since 30m
python3 <skill-dir>/scripts/vercel-logs.py --lines --max 20 -- --deployment <url-or-id>
python3 <skill-dir>/scripts/vercel-logs.py -- --project store-connect --since 2h
```

- Options before `--` belong to the script: `--grep REGEX` filters on path or message, `--lines` prints one line per log instead of groups, `--width N` clips messages (default 220), `--max N` caps lines (default 40).
- Options after `--` go to `vercel logs`: `--since` (default 1h), `--limit` (default 500), `--environment`, `--level`, `--deployment`, `--project`, `--status-code`, `--query`, `--request-id`.
- Start narrow: `--level error` or a `--grep` for the endpoint. Widen only when the narrow run shows nothing.
- To read one full message, rerun with `--lines --grep` on a unique part of it and a larger `--width`.
