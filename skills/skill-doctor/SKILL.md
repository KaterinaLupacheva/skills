---
name: skill-doctor
description: "Grade installed skills by scoring recent Claude Code conversations for efficiency, code quality, procedure compliance, and verbosity, then draft skill edits backed by the conversations that failed. Use when the user asks which skills actually work, wants their agent setup graded from real history, or wants evidence-based skill improvements."
disable-model-invocation: true
metadata:
  credits:
    skill: skill-doctor
    author: Warp
    url: "https://github.com/warpdotdev/common-skills/tree/main/.agents/skills/skill-doctor"
---

# Skill doctor

Score recent local conversations, find the skill gaps behind the ones that went badly, and draft edits. Everything stays on this machine. Never upload transcripts or any excerpt of them.

Let `SKILL_ROOT` be the directory holding this file.

## 1. Scope the run

Check for a git repository with `git rev-parse --show-toplevel`. Then ask two questions with `AskUserQuestion`:

1. **Which conversations should I grade?** Offer "This repository" (recommended inside a repo), "All conversations" (recommended outside one), and "Choose projects". For chosen projects, collect the paths and confirm each is a git repository.
2. **Which skills should I evaluate?** Offer "Project and global skills" (recommended) and "Project skills only".

Create a fresh report directory outside every repository:

```bash
REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/skill-doctor-XXXXXXXX")"
```

## 2. Collect

```bash
python3 "$SKILL_ROOT/scripts/collect_sessions.py" --harness claude --out "$REPORT_DIR" <scope> <skills>
```

- Scope: `--repo "$REPO"` for this repository, one `--repo PATH` per chosen project, or `--all-conversations`.
- Skills: add `--include-global-skills` for project and global skills.
- History comes from `$CLAUDE_CONFIG_DIR/projects`, else `~/.claude/projects`. Grade another config directory with `--claude-home PATH`.
- Other flags: `--days N` (default 45), `--max-sessions N` (default 12), `--skills-dir PATH` (repeatable), `--include-subagents`.

Read `$REPORT_DIR/inventory.json`. If `sessions_sampled` is 0, say there is nothing recent to score, suggest a larger `--days` or another scope, and stop. If `skills_found` is 0, continue. The report then argues for creating skills, and `skill_coverage` is 0.

## 3. Score each transcript

Judge every file in `$REPORT_DIR/transcripts/` against all four rubrics in `$SKILL_ROOT/scorers/`. For each scorer, record the label, its numeric score from the rubric's label table, and a 1 to 3 sentence reason that cites the transcript. Score code quality only where the transcript shows code changes. Otherwise record `insufficient_evidence`, which is left out of the code-quality mean and never fails a conversation.

Score up to 50 transcripts in this conversation. Above 50, split them into batches of about 20 and hand each batch to a parallel subagent. Each subagent gets the rubric paths and its transcript paths, and writes `$REPORT_DIR/scores/<transcript-name>.json`.

## 4. Aggregate

- `raw_<scorer>` is the mean score across sessions for efficiency, code quality, procedure compliance, and verbosity. If no session had code-quality evidence, use 0.5 and say so.
- Curve each mean with `curve(x) = 0.5 + 0.5 * x`.
- `skill_coverage` is the fraction of sampled sessions where at least one installed skill was detected.
- `overall = 0.25 * efficiency + 0.25 * code_quality + 0.2 * procedure_compliance + 0.15 * verbosity + 0.15 * skill_coverage`, using the curved values.
- Grade `overall` with A+ ≥ 0.97, A ≥ 0.93, A- ≥ 0.90, B+ ≥ 0.87, B ≥ 0.83, B- ≥ 0.80, C+ ≥ 0.77, C ≥ 0.73, C- ≥ 0.70, D ≥ 0.60, else F.

A conversation fails when any applicable raw score is below 0.5. Only failed conversations count as evidence for suggestions.

Derive:

- **Top findings.** The 3 most impactful specific patterns across sessions, one or two plain sentences each.
- **Suggestions.** Each names a skill (existing or proposed) and one concrete change, such as a description fix so it triggers, a missing step or check, or a command to encode. Each cites the failed session, the scorer, and the moment that motivated it. An installed skill that should have triggered in a failed conversation but didn't usually has a description problem.

## 5. Draft skill edits

Follow `$SKILL_ROOT/references/skill-improvements.md`. For each suggestion that clears its bar:

1. Read the skill's current file. Its path is in `inventory.json`.
2. Write the improved version to `$REPORT_DIR/proposed/<skill-name>/SKILL.md`, changing only what the evidence justifies.
3. Write `diff -u <current> <proposed>` to `$REPORT_DIR/proposed/<skill-name>.diff`. For a new skill, the proposed file is the whole change.

Never edit the real skill files in this step.

## 6. Report

Write `$REPORT_DIR/report.md` with the grade, a table of the five curved scores as percentages, the session and skill counts from `inventory.json`, the top findings, and each suggestion with its evidence and diff path. Inline diffs shorter than about 40 lines.

Reply with the grade, the three findings, and the absolute path to `report.md`. Then ask whether to apply the suggested edits.
