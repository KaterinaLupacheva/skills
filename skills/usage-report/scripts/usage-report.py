#!/usr/bin/env python3
"""Summarize Claude Code token use from session transcripts, as compact Markdown.

  usage-report.py [--days 7] [--config-dir DIR ...] [--skills-dir DIR] [--history DIR]

Reads <config-dir>/projects/**/*.jsonl for every config dir (default: every ~/.claude* dir that has
a projects/ folder). Saves a JSON summary per run in --history (default ~/.claude-usage-reports) and
prints the change against the previous run.
"""
import argparse
import collections
import glob
import json
import os
import re
import statistics
import time
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
parser.add_argument("--days", type=float, default=7)
parser.add_argument("--config-dir", action="append")
parser.add_argument("--skills-dir", help="repo skills folder to list unused skills from (default: target of <config-dir>/skills)")
parser.add_argument("--history", default="~/.claude-usage-reports")
args = parser.parse_args()

home = os.path.expanduser("~")
config_dirs = [os.path.expanduser(d) for d in args.config_dir] if args.config_dir else sorted(
    d for d in glob.glob(os.path.join(home, ".claude*")) if os.path.isdir(os.path.join(d, "projects")))
since = time.time() - args.days * 86400
cutoff = datetime.fromtimestamp(since, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
TOKEN_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
CONTEXT_TYPES = {"skill_listing", "deferred_tools_delta", "mcp_instructions_delta", "instructions", "agent_listing_delta", "hook_success"}


def workspace_name(d):
    return os.path.basename(d).lstrip(".") or d


def size(content):
    return len(content) if isinstance(content, str) else len(json.dumps(content))


def short(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def bash_kind(cmd):
    if re.search(r"vitest|jest|gates|tsc|lint|\btest\b|typecheck|type-check", cmd):
        return "tests/checks"
    if re.search(r"git (diff|show|log)", cmd):
        return "git diff/show/log"
    if re.search(r"(^|[;&|(] *)(cat|sed -n|head|tail|less) ", cmd):
        return "read file (cat/sed/head)"
    if "grep" in cmd or re.search(r"\brg\b", cmd):
        return "grep"
    if re.search(r"\bgh\b", cmd):
        return "gh"
    return "other"


sessions = []
for cfg in config_dirs:
    ws = workspace_name(cfg)
    for path in glob.glob(os.path.join(cfg, "projects", "**", "*.jsonl"), recursive=True):
        if os.path.getmtime(path) < since:
            continue
        rel = os.path.relpath(path, os.path.join(cfg, "projects"))
        s = dict(ws=ws, cfg=cfg, project=re.sub(r"^-Users-[^-]+-", "", rel.split(os.sep)[0]), path=path,
                 sub="/subagents/" in path.replace(os.sep, "/"), tok=collections.Counter(), models=collections.Counter(),
                 calls=0, first_ctx=None, slash=[], skill_tool=[], skill_reads=collections.Counter(), tools=collections.Counter(),
                 tool_out=collections.Counter(), bash_out=collections.Counter(), bash_n=collections.Counter(), big=[], prompts=[],
                 agents=[], attach=collections.Counter(), persisted=0, start=None)
        seen, uses = set(), {}
        try:
            lines = open(path, errors="ignore")
        except OSError:
            continue
        for line in lines:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = d.get("timestamp") or ""
            if ts < cutoff:
                continue
            s["start"] = min(s["start"] or ts, ts)
            if d.get("type") == "attachment":
                a = d.get("attachment") or {}
                if a.get("type") in CONTEXT_TYPES:
                    s["attach"][a["type"] + (":" + a.get("hookName", "") if a.get("type") == "hook_success" else "")] += size(a)
                continue
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            content = m.get("content")
            if d.get("type") == "user":
                if isinstance(content, str):
                    s["slash"] += [c.strip() for c in re.findall(r"<command-name>/?([^<]+)</command-name>", content)]
                    arg = re.search(r"<command-args>(.*?)</command-args>", content, re.S)
                    if not content.startswith("<") and not d.get("isMeta"):
                        s["prompts"].append(content)
                    elif arg and arg.group(1).strip():
                        s["prompts"].append(arg.group(1))
                elif isinstance(content, list):
                    for x in content:
                        if not isinstance(x, dict):
                            continue
                        if x.get("type") == "text":
                            t = x.get("text", "")
                            if not t.startswith(("<", "Base directory for this skill")) and not d.get("isMeta") and not d.get("isCompactSummary"):
                                s["prompts"].append(t)
                        elif x.get("type") == "tool_result":
                            n = size(x.get("content"))
                            name, inp = uses.get(x.get("tool_use_id"), ("?", ""))
                            s["tool_out"][name] += n
                            if name == "Bash":
                                kind = bash_kind(inp)
                                s["bash_out"][kind] += n
                                s["bash_n"][kind] += 1
                            text = x.get("content") if isinstance(x.get("content"), str) else json.dumps(x.get("content"))
                            if "tool-results/" in text and re.search(r"too large|saved to", text, re.I):
                                s["persisted"] += 1
                            if n > 20000 and not re.search(r"\.(png|jpe?g|gif|webp)\b", inp, re.I):
                                s["big"].append((n, name, inp))
            elif d.get("type") == "assistant":
                mid = m.get("id")
                if mid not in seen:
                    seen.add(mid)
                    u = m.get("usage") or {}
                    for k in TOKEN_KEYS:
                        s["tok"][k] += u.get(k) or 0
                    ctx = sum(u.get(k) or 0 for k in TOKEN_KEYS if k != "output_tokens")
                    if ctx and s["first_ctx"] is None:
                        s["first_ctx"] = ctx
                    s["models"][m.get("model")] += 1
                    s["calls"] += 1
                for x in content or []:
                    if not isinstance(x, dict) or x.get("type") != "tool_use":
                        continue
                    name, inp = x.get("name", "?"), x.get("input") or {}
                    s["tools"][name] += 1
                    flat = inp.get("command") if name == "Bash" else json.dumps(inp)
                    uses[x.get("id")] = (name, flat or "")
                    if name == "Skill":
                        s["skill_tool"].append(inp.get("skill", ""))
                    elif name in ("Agent", "Task"):
                        s["agents"].append(inp.get("subagent_type") or "general-purpose")
                    for sk in set(re.findall(r"/skills/([\w:-]+)/", flat or "")):
                        if not re.fullmatch(r"[0-9a-f-]{36}|skills", sk):
                            s["skill_reads"][sk] += 1
        if s["start"]:
            sessions.append(s)

main = [s for s in sessions if not s["sub"]]
subs = [s for s in sessions if s["sub"]]
total = lambda s: sum(s["tok"].values())
fmt = lambda n: f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k" if n >= 1e3 else str(int(n))
out = []
P = out.append

grand = sum(total(s) for s in sessions)
cache_read = sum(s["tok"]["cache_read_input_tokens"] for s in sessions)
calls = sum(s["calls"] for s in main)
P(f"# Usage report: last {args.days:g} days (since {cutoff[:10]})\n")
P(f"- Sessions: {len(main)} main, {len(subs)} subagent transcripts. Config dirs: {', '.join(workspace_name(c) for c in config_dirs)}")
P(f"- Tokens: {fmt(grand)} total; cache read {fmt(cache_read)} ({cache_read * 100 // max(grand, 1)}%), cache write "
  f"{fmt(sum(s['tok']['cache_creation_input_tokens'] for s in sessions))}, output {fmt(sum(s['tok']['output_tokens'] for s in sessions))}")
P(f"- Main-thread model calls: {calls}; average context per call {fmt(sum(total(s) - s['tok']['output_tokens'] for s in main) // max(calls, 1))}")
P(f"- Subagents: {fmt(sum(total(s) for s in subs))} ({sum(total(s) for s in subs) * 100 // max(grand, 1)}%)\n")

P("## By workspace and project\n")
P("| Workspace | Project | Sessions | Tokens | Avg/session | Avg ctx/call | Starting ctx (median) |")
P("|---|---|---|---|---|---|---|")
groups = collections.defaultdict(list)
for s in sessions:
    groups[(s["ws"], s["project"])].append(s)
for (ws, proj), ss in sorted(groups.items(), key=lambda kv: -sum(total(s) for s in kv[1])):
    m_ = [s for s in ss if not s["sub"]]
    c = sum(s["calls"] for s in m_)
    starts = [s["first_ctx"] for s in m_ if s["first_ctx"]]
    P(f"| {ws} | {proj} | {len(m_)} | {fmt(sum(total(s) for s in ss))} | {fmt(sum(total(s) for s in ss) // max(len(m_), 1))} | "
      f"{fmt(sum(total(s) - s['tok']['output_tokens'] for s in m_) // max(c, 1))} | {fmt(statistics.median(starts)) if starts else '-'} |")

P("\n## Fixed context per session (chars of attachments, average per main session)\n")
for ws in sorted({s["ws"] for s in main}):
    ms = [s for s in main if s["ws"] == ws]
    agg = collections.Counter()
    for s in ms:
        agg.update(s["attach"])
    starts = sorted(s["first_ctx"] for s in ms if s["first_ctx"])
    parts = ", ".join(f"{k} {fmt(v // len(ms))}" for k, v in agg.most_common(6))
    P(f"- **{ws}** (starting context median {fmt(starts[len(starts) // 2]) if starts else '-'} tokens): {parts}")
for cfg in config_dirs:
    for mem in glob.glob(os.path.join(cfg, "projects", "*", "memory", "MEMORY.md")):
        n = os.path.getsize(mem)
        if n > 3000:
            P(f"- Large memory index: {workspace_name(cfg)}/{os.path.basename(os.path.dirname(os.path.dirname(mem)))} MEMORY.md = {fmt(n)} chars")
    for name in ("CLAUDE.md",):
        f = os.path.join(cfg, name)
        if os.path.exists(f) and os.path.getsize(f) > 4000:
            P(f"- Large user {name} in {workspace_name(cfg)}: {fmt(os.path.getsize(f))} chars")

P("\n## Skills\n")
inv, sess_count, reads, wss = collections.Counter(), collections.Counter(), collections.Counter(), collections.defaultdict(set)
repeats = 0
BUILTIN = {"clear", "model", "login", "logout", "mcp", "compact", "resume", "config", "status", "cost", "context", "exit", "help", "skills", "plugin", "init", "memory", "rewind", "usage"}
for s in sessions:
    names = [n for n in s["slash"] + s["skill_tool"] if n not in BUILTIN]
    for n in names:
        inv[n] += 1
        wss[n].add(s["ws"])
    for n in set(names):
        sess_count[n] += 1
    for n, c in collections.Counter(s["slash"]).items():
        if n not in BUILTIN and c > 1:
            repeats += c - 1
    for n, c in s["skill_reads"].items():
        reads[n] += c
        wss[n].add(s["ws"])
P("| Skill | Invocations | Sessions | File reads | Workspaces |")
P("|---|---|---|---|---|")
for n in sorted(set(inv) | set(reads), key=lambda n: (-inv[n], -reads[n])):
    P(f"| {n} | {inv[n]} | {sess_count[n]} | {reads[n]} | {', '.join(sorted(wss[n]))} |")
P(f"\n- Same skill re-invoked by slash command inside one session: {repeats} times")
skills_dir = args.skills_dir or next((os.path.realpath(os.path.join(c, "skills")) for c in config_dirs if os.path.isdir(os.path.join(c, "skills"))), None)
if skills_dir and os.path.isdir(skills_dir):
    repo = sorted(d for d in os.listdir(skills_dir) if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md")))
    unused = [n for n in repo if not inv[n] and not reads[n]]
    auto_unused = []
    for n in unused:
        head = open(os.path.join(skills_dir, n, "SKILL.md"), errors="ignore").read(3000)
        if "disable-model-invocation: true" not in head:
            auto_unused.append(n)
    P(f"- Skills in {skills_dir}: {len(repo)}; unused in this window: {len(unused)}")
    P(f"- Unused and model-invocable (their descriptions load in every session): {', '.join(auto_unused) or 'none'}")
    P(f"- Unused: {', '.join(unused) or 'none'}")

P("\n## Tools\n")
tools, tout, bout, bn = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
for s in sessions:
    tools.update(s["tools"])
    tout.update(s["tool_out"])
    bout.update(s["bash_out"])
    bn.update(s["bash_n"])
P("- Calls: " + ", ".join(f"{k} {v}" for k, v in tools.most_common(15)))
P("- Output chars by tool: " + ", ".join(f"{k} {fmt(v)}" for k, v in tout.most_common(10)))
P("- Bash output by kind: " + ", ".join(f"{k} {bn[k]} calls/{fmt(v)}" for k, v in bout.most_common()))
P("- Image reads are left out of the largest outputs: the API bills an image by its pixels, not its base64 size.")
P(f"- Outputs too large and saved to disk: {sum(s['persisted'] for s in sessions)}")
big = sorted((b for s in sessions for b in s["big"]), reverse=True)[:12]
if big:
    P("- Largest tool outputs:")
    for n, name, inp in big:
        P(f"  - {fmt(n)} chars, {name}: `{short(inp, 110)}`")

P("\n## Subagents\n")
by = collections.Counter()
for s in subs:
    by[max(s["models"], key=s["models"].get) if s["models"] else "?"] += total(s)
P("- Tokens by model: " + ", ".join(f"{k} {fmt(v)}" for k, v in by.most_common()))
agents = collections.Counter(a for s in main for a in s["agents"])
P("- Spawns by type: " + (", ".join(f"{k} {v}" for k, v in agents.most_common()) or "none"))
parent_skill = collections.Counter()
for s in subs:
    parent = next((p for p in main if s["path"].startswith(p["path"][:-6])), None)
    tag = ", ".join(sorted(set(n for n in (parent["slash"] + parent["skill_tool"]) if n not in BUILTIN))) if parent else "?"
    parent_skill[tag or "no skill"] += total(s)
P("- Tokens by parent session's skills: " + ", ".join(f"[{k}] {fmt(v)}" for k, v in parent_skill.most_common(6)))

P("\n## Top sessions\n")
for s in sorted(main, key=lambda s: -total(s))[:12]:
    sub_tok = sum(total(x) for x in subs if x["path"].startswith(s["path"][:-6]))
    skills = ",".join(sorted(set(n for n in s["slash"] + s["skill_tool"] if n not in BUILTIN)))
    P(f"- {fmt(total(s))} (+{fmt(sub_tok)} sub) {s['ws']}/{s['project']} {s['start'][:10]} calls={s['calls']} [{skills}] {short((s['prompts'] or [''])[0], 90)!r}")

P("\n## Repeated prompts (follow-ups that could be automated)\n")
norm = collections.Counter()
for s in main:
    for p in s["prompts"][1:]:
        k = re.sub(r"[^a-z ]", "", " ".join(p.lower().split()[:7]))
        if len(k) > 8:
            norm[k] += 1
P(", ".join(f"'{k}' x{v}" for k, v in norm.most_common(12) if v >= 3) or "none")

summary = {
    "date": datetime.now().strftime("%Y-%m-%d"), "days": args.days, "tokens": grand, "cache_read": cache_read,
    "main_sessions": len(main), "calls": calls, "subagent_tokens": sum(total(s) for s in subs),
    "starting_ctx": {ws: statistics.median([s["first_ctx"] for s in main if s["ws"] == ws and s["first_ctx"]] or [0]) for ws in {s["ws"] for s in main}},
}
hist = os.path.expanduser(args.history)
os.makedirs(hist, exist_ok=True)
previous = sorted(f for f in glob.glob(os.path.join(hist, "*.json")) if not f.endswith(summary["date"] + ".json"))
if previous:
    prev = json.load(open(previous[-1]))
    per = lambda d, k: d[k] / max(d["main_sessions"], 1)
    P(f"\n## Change since {prev['date']}\n")
    P(f"- Tokens per main session: {fmt(per(prev, 'tokens'))} → {fmt(per(summary, 'tokens'))}")
    P(f"- Calls per main session: {per(prev, 'calls'):.0f} → {per(summary, 'calls'):.0f}")
    P(f"- Subagent tokens: {fmt(prev['subagent_tokens'])} → {fmt(summary['subagent_tokens'])}")
    for ws, v in summary["starting_ctx"].items():
        if ws in prev.get("starting_ctx", {}):
            P(f"- Starting context {ws}: {fmt(prev['starting_ctx'][ws])} → {fmt(v)}")
json.dump(summary, open(os.path.join(hist, summary["date"] + ".json"), "w"), indent=2)
print("\n".join(out))
