---
name: setup-pstack
description: Configure which models pstack uses per role. Detects your available models and writes a model configuration file that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", or changing pstack's model choices.
---

# Setup pstack

Write `~/.claude/pstack-models.md`, the file that sets pstack's model per role. Every pstack skill reads it when present and falls back to its own default otherwise.

## Steps

### 1. Detect available models

Read the `model` parameter of the subagent-spawning tool in this session (the `Agent` tool, named `Task` in some builds) and enumerate the values its schema accepts. That enum is the dependable source, and in Claude Code it is a short list of aliases such as `opus`, `sonnet`, and `haiku`, not vendor slugs. Run `claude --help` or check `~/.claude/settings.json` only as a cross-check. If you cannot detect any, ask the user which models they have access to. Never write a value you have not confirmed the tool accepts. The aliases `inherit-parent` and `auto` are always valid even though they are not detected values.

### 2. Load current state

The default role-to-model mapping is the file shape shown in step 5 below. If `~/.claude/pstack-models.md` already exists, read it and treat its values as the current choices. Otherwise start from those defaults. A line whose role is not in step 5, such as `how critics`, is from a retired role. Drop it.

### 3. Map and confirm

Show every role with its current model, marking any value not in the detected enum as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models plus `inherit-parent` and `auto` (both mean: this role runs on the parent chat model, which is how Auto users stay on Auto) as the options. Prefer AskUserQuestion over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count. `arena cross-judge pool` is also a list, but Arena runs one judge. It tries only values other than the parent's model, in list order, so order it by preference. An `inherit-parent` or `auto` value never judges. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every real model value written must be in the detected enum. `inherit-parent` and `auto` always pass. If a chosen value is not available, stop and ask again.

### 5. Write the file

Write `~/.claude/pstack-models.md` with one line per role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent. Shape:

```
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit the subagent `model`). Alias entries in a panel list still count toward its fan-out.
feature, refactoring: sonnet
bug-fix: sonnet
perf-issue: sonnet
hillclimb: sonnet
judgment and prose: opus
hardest tasks: opus
how explorer: haiku
how explainer: opus
why investigators: haiku
why synthesizer: opus
reflect tooling: opus
reflect judgment, divergent, synthesizer: opus
arena runners: opus, sonnet
arena cross-judge pool: opus, sonnet
swarm workers: haiku
architect runners: opus, sonnet
interrogate reviewers: opus, sonnet
```

Every panel here runs on one vendor's models, so the arms differ by capability and framing rather than by vendor. A repeated model in a panel is fine: two `opus` arms on different briefs count as two arms. Where a panel entry is weaker than the work deserves (`sonnet` on a hard design bakeoff), promote it to another `opus` arm with its own brief instead of dropping the arm.

### 6. Confirm

Tell the user the file was written and that pstack skills read it on their next run. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke `/create-verification-skill` (resolves wherever pstack is installed: workspace, user, or plugin). On no, move on without pushing.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill." On yes, invoke `/create-formal-verification-skill` (resolves wherever pstack is installed: workspace, user, or plugin). On no, move on without pushing.
