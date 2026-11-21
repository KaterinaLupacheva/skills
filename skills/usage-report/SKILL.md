---
name: usage-report
description: Review Claude Code token use across every config dir and project, and recommend cuts.
disable-model-invocation: true
argument-hint: "[days]"
---

# Usage report

Find where the tokens go and what to cut. Most tokens are cache reads: every model call rereads the whole context. So the levers are a smaller fixed context per session, fewer calls in sessions with a large context, and less tool output kept in context.

## Steps

1. **Run the script.** One call, no other reading first:

   ```
   python3 <skill-dir>/scripts/usage-report.py --days <days, default 7>
   ```

   It reads `projects/**/*.jsonl` in every `~/.claude*` dir and prints a Markdown summary of about 3k tokens. Pass `--config-dir` to limit it. It saves a summary to `~/.claude-usage-reports/` and prints the change since the previous run. Never read transcripts by hand: one transcript can be megabytes.

2. **Check the causes.** Look at what the summary points to, with a targeted command, never a whole file. Use the table below.

3. **Reply.** In this order:
   - **Change since the last run**, if the script printed it: what moved, and which earlier fix it reflects.
   - **Where the tokens go**: workspace and project totals, starting context per workspace, subagent share.
   - **Recommendations**, ranked by tokens saved. For each: the evidence number, the fix, and who does it (you, or the user in `/mcp` or claude.ai settings).
   - **Skill usage table** from the script, and the unused skills. Note that a skill with `disable-model-invocation: true` costs nothing until it is called, so unused skills cost tokens only if they are model-invocable.

   Change nothing until the user picks the recommendations to do.

## Causes and fixes

| Signal in the report | Check | Fix |
|---|---|---|
| A workspace starts much higher than the others | Its `settings.json` plugins and the `hook_success:SessionStart` size | Disable a plugin whose hook injects context; keep its MCP server with `claude mcp add`. |
| Large `deferred_tools_delta` | `claude mcp list` in that workspace | Turn off unused connectors in every project: `python3 <skill-dir>/scripts/disable-connectors.py --config-dir <dir> --keep "<connector>"`. Rerun it for new project folders. |
| Large memory index | The `MEMORY.md` lines | Move notes on shipped tickets and past incidents to `memory/archive/` with an `ARCHIVE.md` index, and leave one pointer line. Keep preference notes, warnings, invariants and open work. |
| `Read` or `cat` of large docs, or many outputs saved to disk | The paths in the largest outputs | Split big plan docs (step-plan keeps decisions in `decisions.md`). A user `CLAUDE.md` rule: check size first and read ranges. |
| Big MCP payloads | The tool name | Use a tool or script that returns fewer fields, for example the `vercel-logs` skill for logs. |
| Same skill re-invoked in one session | The count | Tell the user: type the slash command once per session. |
| Subagent tokens mostly on the strongest model | The parent skill in the report | Set `model: sonnet` or `haiku` for that skill's volume work. Keep the strongest model for judgment. |
| Repeated follow-up prompts | The prompts | Make the skill print what the user keeps asking for, at the end of its reply. |
| Sessions with 150+ calls | The first prompt | Suggest splitting the work, or `/clear` between unrelated tasks. |
