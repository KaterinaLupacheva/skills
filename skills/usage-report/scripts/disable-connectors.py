#!/usr/bin/env python3
"""Turn off every claude.ai connector except the kept ones, in every project of one Claude Code config dir.

  disable-connectors.py --config-dir ~/.claude-SH --keep "claude.ai Atlassian MCP" [project-dir ...]

Claude Code stores connector switches per project, so a new project folder starts with every
connector on. Run this again after opening Claude Code in a new folder, or pass the folder.
Restart Claude Code afterwards. Safe to run more than once.
"""
import argparse
import json
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("--config-dir", required=True, help="CLAUDE_CONFIG_DIR, for example ~/.claude-SH")
parser.add_argument("--keep", action="append", default=[], help='connector to leave on, for example "claude.ai Atlassian MCP"')
parser.add_argument("projects", nargs="*", help="project folders to add even if Claude Code has not opened them yet")
args = parser.parse_args()

config_dir = os.path.expanduser(args.config_dir)
config_path = os.path.join(config_dir, ".claude.json")
keep = set(args.keep)
keep_lower = {k.lower() for k in keep}


def seen_connectors(config):
    names = set(config.get("claudeAiMcpEverConnected") or [])
    for root, _, files in os.walk(os.path.join(config_dir, "projects")):
        for f in files:
            if not f.endswith(".jsonl"):
                continue
            with open(os.path.join(root, f), errors="ignore") as fh:
                for line in fh:
                    if "claude_ai_" in line:
                        names.update("claude.ai " + m.replace("_", " ") for m in re.findall(r"mcp__claude_ai_([A-Za-z0-9_.-]+?)__", line))
    names |= {n.replace("monday com", "monday.com") for n in names}
    names |= {re.sub(r" (\d+)$", r" (\1)", n) for n in names}
    return names


config = json.load(open(config_path))
off = sorted(n for n in seen_connectors(config) if n.lower() not in keep_lower)
projects = config.setdefault("projects", {})
for extra in args.projects:
    projects.setdefault(os.path.abspath(os.path.expanduser(extra)), {})
for project in projects.values():
    current = [n for n in project.get("disabledMcpServers") or [] if n.lower() not in keep_lower]
    project["disabledMcpServers"] = current + [n for n in off if n not in current]
json.dump(config, open(config_path, "w"), indent=2)
print(f"{len(off)} connectors off in {len(projects)} projects. Kept on: {', '.join(sorted(keep)) or 'none'}")
