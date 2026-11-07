---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Before fanning out, find this conversation's transcript. Claude Code stores transcripts at `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/<uuid>.jsonl`, where `<slug>` is the absolute workspace path with every "/" turned into "-" (so `/Users/you/proj` becomes `-Users-you-proj`). Derive the slug from the current working directory and stay inside that one directory. Do not glob across `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.

```bash
ls -t ${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/*.jsonl ${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/*/subagents/*.jsonl 2>/dev/null | head -10
```

That covers the session itself (`<id>.jsonl`) and its subagents (`<parent-id>/subagents/<child-id>.jsonl`). For each candidate, read the first JSONL line. Take the file whose `message.content[0].text` contains the conversation's opening user prompt. If none matches, pass a tight digest of the session instead.

## 2. Spawn three reviewers in parallel

One message, three `Agent` calls, `subagent_type: general-purpose`. Reviewers need MCP access to look up the tickets, chat threads, and observability traces the transcript references, and subagents inherit the session's MCP servers.

Each reviewer and the synthesizer name a role line in `~/.claude/pstack-models.md` and a default. Set `model` to that line's value, or to the default if the file or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the `Agent` tool rejects a value, use the default and say so. Pick each subagent's `effort` for the job, per the Subagents section of the **poteto-mode** skill.

| Lens | Role line | Default `model` | Prompt template |
|---|---|---|---|
| Judgment | `reflect judgment, divergent, synthesizer` | `opus` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `opus` | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | `opus` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the subagent's final report.

## 3. Synthesize

One `Agent` call, `subagent_type: general-purpose`, `model` from the `reflect judgment, divergent, synthesizer` line (default `opus`). It spot-verifies citations through MCP, which subagents inherit. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **encode-lessons-in-structure** principle skill.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting. Only the Accepted list waits for approval.

Never edit a skill under `plugins/cache/`. Before approval, show its destination, `.claude/skills/<skill>/` or `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/<skill>/`. After approval, copy the skill folder there and edit the copy. Never open a PR or push.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): follow the **Authoring or modifying a skill** playbook (`poteto-mode/playbooks/authoring-a-skill.md`) and run its draft / validate / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): rewrite the `description` frontmatter so it names the triggering phrasings, then re-test it against the prompts that missed.
- `new skill: <kebab-name>`: create it per the **Authoring or modifying a skill** playbook (`poteto-mode/playbooks/authoring-a-skill.md`). Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
