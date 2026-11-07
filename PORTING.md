# Porting pstack to Claude Code

`update-pstack.sh` pulls the pstack skills, and upstream's agents into `agents-upstream/`, from [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack) verbatim. Upstream targets Cursor, so every sync overwrites the Claude Code port and it has to be re-applied. This file is the checklist. Work through it with `git diff` after a sync.

A three-way merge keeps most of the port instead of redoing it. Clone cursor/plugins, then for each pstack file upstream changed since `PSTACK_UPSTREAM`, run `git merge-file skills/<path> <upstream old> <upstream new>`. Only lines both sides touched conflict, and each conflict is a place to re-apply the mappings below. Copy added files in whole and port them by hand.

## Paths

Each workspace sets `CLAUDE_CONFIG_DIR` (`~/.claude-work`, `~/.claude-personal`), and Claude Code reads skills, agents, plugins, and transcripts from there, not from `~/.claude`. Write those paths as `${CLAUDE_CONFIG_DIR:-~/.claude}/...` so they resolve in every workspace and fall back for a plain `claude`.

| Cursor | Claude Code |
|---|---|
| `~/.cursor/skills/<name>/`, `.cursor/skills/<name>/` | `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/<name>/`, `.claude/skills/<name>/` |
| `~/.cursor/plugins/` | `${CLAUDE_CONFIG_DIR:-~/.claude}/plugins/` |
| `~/.cursor/rules/pstack-models.mdc` (always-applied rule) | `~/.claude/pstack-models.md`, read on demand by each skill. Deliberately a fixed path, so both workspaces share one model config. |
| `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl` | `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/<uuid>.jsonl`, subagent runs under `<uuid>/subagents/` |

The Claude Code transcript slug is the absolute working directory with every `/` turned into `-`, leading separator included: `/Users/you/proj` becomes `-Users-you-proj`. Cursor drops the leading slash, Claude Code keeps it as a leading `-`.

## Models

Claude Code spawns Claude models only. The subagent tool's `model` enum is the authority (`opus`, `sonnet`, `haiku` at the time of writing), not vendor slugs. `fable` is deliberately unused.

| Upstream slug | Port |
|---|---|
| `claude-opus-5-5-xhigh`, `claude-opus-5-5-max`, `gpt-5.6-sol-max` (and older `claude-fable-*`, `claude-opus-*` slugs at any effort) | `opus` |
| `grok-4.7-xhigh-fast`, code delegate (feature, refactoring, bug-fix, perf-issue, hillclimb) | `sonnet` |
| `grok-4.7-xhigh-fast`, read-only grunt work (swarm workers, why investigators, how explorer) | `haiku` |
| `grok-4.7-xhigh-fast`, a panel seat (arena, architect, interrogate) | `sonnet` |
| `grok-4.7-xhigh-fast`, reflect tooling | `opus`. Judging what tools a session should have used is judgment work, so the port keeps it on `opus`. |

Panels that upstream fills with one model per vendor (arena runners, architect runners, interrogate reviewers: Claude and Grok) become `opus, sonnet`, with `sonnet` in Grok's seat. When upstream had a GPT seat too, it became a second `opus` arm on a different brief. Upstream's per-spawn "reasoning level and fast or standard speed" becomes the `Agent` tool's `effort` parameter (`low` to `max`, starting at `xhigh`). Claude Code has no per-spawn fast mode, so speed is dropped, and the family-only rules for `cursor-grok-*` and `composer-*` slugs go with the Grok seat. Upstream's "fall back to the same family's default" rule for a rejected slug becomes "fall back to the table default". Wherever a skill asks for "a different model family", the port asks for a different model plus a different brief, since vendor diversity is not available. Arena's cross-judge rule ("never from the parent's family", family-ordered fallbacks) becomes "never on the parent's model": an `opus` parent gets `sonnet`, any other parent gets `opus` first.

## Subagents

- `Task` tool → the `Agent` tool (still named `Task` in some builds). Skills say both.
- `subagent_type: generalPurpose` → `general-purpose`.
- `subagent_type: "poteto-agent"` / `"Comment Sicko"` → `poteto-agent` / `comment-sicko`, from this repo's `agents/` directory. Both workspaces link `<config dir>/agents` to this repo's `agents/`, as they do for `skills`. A project's `.claude/agents/` also works, or fall back to `general-purpose` with the agent file as the brief.
- `readonly: true` → no such parameter. Say "read-only" in the brief, or use the `Explore` agent type.
- `readonly: false` ("agent mode", needed upstream so MCP survives) → drop it. Claude Code subagents inherit the session's MCP servers.
- `environment: "cloud"` / `"local"`, `cloud_base_branch` → `isolation: "worktree"` for parallel writers, `isolation: "remote"` where cloud agents are enabled, plain local otherwise. A worktree agent checks out its own base branch.
- `run_in_background: true` → drop. Subagents already run in the background.
- Resuming an agent → `SendMessage`. Listing them → `ListAgents` or `/tasks`.
- "Fork" a worker to reuse its built state (Orchestrate) → continue that worker with `SendMessage`. Claude Code's `fork` subagent type copies the parent's context, not a worker's checkout, so it is not the same thing.

## Tools and skills that do not exist in Claude Code

- `AskQuestion` → `AskUserQuestion`.
- Cursor's built-in `create-skill` → `skills/poteto-mode/playbooks/authoring-a-skill.md`, which carries the Claude Code skill format.
- Cursor's built-in `babysit` → this repo's Babysit playbook owns those requests.
- `deslop` from `cursor-team-kit` → this repo's `unslop` skill.
- Cursor's `/visualize` charts → the **dataviz** skill.
- "A Cursor cloud agent" as an owner or verifier → one agent in its own `isolation: "worktree"` checkout, or `isolation: "remote"` where cloud agents are available. "Assume the VM dies" becomes "Assume the agent dies", and "the root agent's store" becomes the root's scratchpad directory, which a remote agent cannot reach, so it returns its trail with each report.
- Cursor's Project tracker (`notes.md`) and Project store (Orchestrate) → a `notes.md` tracker in the scratchpad directory the system prompt names, or a git-ignored repo directory when the program must outlive the session, same as the multi-phase plan file.
- poteto-agent's search of `~/.cursor/plugins/` for `poteto-mode/SKILL.md` → `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/poteto-mode/SKILL.md`, then `.claude/skills/poteto-mode/SKILL.md`.
- `control-ui` / `control-cli` from `cursor-team-kit` → the project's `verify-*` skill (`/create-verification-skill` generates one), or Claude in Chrome for browser UIs.
- MCP discovery through Cursor's `mcps/` directory → MCP tools are exposed as `mcp__<server>__<tool>`; cross-check with `claude mcp list`.
- `/loop` exists in both, so only the attribution changes. `/loop 1h` works as written.
- Re-reading a playbook "from trunk" with `git show origin/main:pstack/skills/<path>` → `$PSTACK/<path>`, where `$PSTACK` is `${CLAUDE_CONFIG_DIR:-~/.claude}/skills` (or `.claude/skills`), or `git show origin/main:<path>` where a repo vendors the skills.
- "One Cursor cloud agent per PR" → one agent per PR in its own `isolation: "worktree"` checkout, or `isolation: "remote"` where cloud agents are available.
- Upstream's `docs/guide/`, `docs/harness/claude-code.md`, and `README.md` are not synced. `poteto-help` links the guide pages on GitHub instead of `../../docs/guide/`. The harness adapter targets the `pstack:`-prefixed plugin install, not this repo.

## Frontmatter

Claude Code requires `name` to be lowercase kebab-case matching the directory. Cursor-only keys get dropped: `mode`, `icon`, `color`, `reminder` (poteto-mode, whose reminder moved into the body), and `paths` (typescript-best-practices, which now relies on its description to trigger).

## setup-pstack budget

Upstream's `/setup-pstack` asks for a reasoning budget (`unlimited`, `large`, `medium`, `small`) and rewrites the effort token of every slug (`-max`, `-xhigh`, ...). Claude Code's `model` values are bare aliases with no effort token, so the budget step and the `# budget` line are dropped. Each spawn sets `effort` itself, per poteto-mode's "Match the effort to the job" paragraph. Keep the "drop retired role lines" rule.

## poteto-help

Upstream's `poteto-help` explains Cursor install (`/add-plugin`), Custom Modes (Option+Enter), and Cursor's built-ins. The port says the skills come from this repo, that Claude Code has no Custom Modes so each task starts with `/poteto-mode`, and points not-in-pstack questions at `unslop`, `verify-*`, and Claude in Chrome. Remove the `make-bot-ui` row from its table after every sync.

## Renamed skills

Matt Pocock's skills (`update-mattpocock.sh`) own the names `tdd` and `teach` here, so `update-pstack.sh` writes pstack's versions to `skills/pstack-tdd/` and `skills/pstack-teach/`. After every sync, set their frontmatter `name` to match, and point pstack's references at the new names: the `tdd` skill in `poteto-mode/playbooks/bug-fix.md`, and `/tdd` and `/teach` in `poteto-help` (`SKILL.md`, `references/recipes.md`, `references/prompting.md`).

## Local rule: no commits, no PRs

Not part of the Cursor port, but re-applied the same way. poteto-mode never commits, pushes, or opens a PR unless the user asks in that session. It lives in three places: the `## No commits, no PRs` section near the top of `poteto-mode/SKILL.md`, the skip line at the top of `poteto-mode/playbooks/opening-a-pr.md`, and the matching paragraph in `agents/poteto-agent.md`. `check-port.sh` fails if a sync drops any of them.

## Not portable

`make-bot-ui` drives Cursor automations end to end: the `update_state` routine tool, `api2.cursor.sh` webhook URLs, `SendToUser` secret-request cards. None of them exist in Claude Code, so the skill is deleted here, and `update-pstack.sh` skips it.
