---
name: step-plan
description: Implementation plan as a folder of one-session step files with checkbox done-criteria and numbered decisions. Use when work needs more than one session or waits on something the agent cannot do, or the user asks for an implementation plan.
---

# Step plan

A step plan is a folder: a `README.md` that holds the decisions every step relies on, and one file per step. One step is one session and one verifiable unit. Every step ends on checkboxes, and a box is checked only when its evidence exists.

You own the plan, not the code. Write no implementation in this session.

## Steps

1. **Decide whether a plan pays.** Write one when the work needs more than one session, or when a step depends on something outside the agent: a credential, test data, a check only the user can run, an answer from another person. Otherwise say the work fits one session and stop.
2. **Explore.** Send bulk reading to subagents and keep their summaries. Done when every area the change touches has a `file:line` pointer, a prior-art file to copy, and the repo's typecheck, test and lint commands are known.
3. **Settle the decisions.** List every open question. Answer what the code can answer by reading it. Run `/grill-with-docs` for the rest (it loads the `grilling` and `domain-modeling` skills; load those two if you cannot run it). For every decision table, list each combination of input states, including states the system is already in (connected, half-migrated, previously deleted). Each missing row is an open question. Done when zero questions remain and each decision has a number, the rule, the reason, and its `file:line` references.
4. **Collect the blockers.** List everything a step needs that the agent cannot do or fetch itself. Ask the user about each one now. Done when each blocker is resolved, or recorded with an owner.
5. **Cut the steps.** Each step is one session and one verifiable unit, ordered by dependency. A step that changes real data or calls a live destructive API runs alone and last, after the user confirms it in that session.
6. **Write the files.** Create `docs/plans/<ticket-or-slug>/` in the project and add `docs/plans/` to `.git/info/exclude`, so the plan survives sessions and stays out of commits. Copy [`templates/README.md`](templates/README.md) to `README.md` and [`templates/step.md`](templates/step.md) to `NN-<slug>.md` per step, and fill every placeholder.
7. **Check the plan.** Done when all of these hold:
   - Every Build item is covered by a Tests box or a Verify box.
   - Every box carries a tag from **Box tags** in the README.
   - Every `[needs: X]` box has its X in **Blockers**.
   - Every decision is named in the **Read decisions** line of at least one step, and each step names every decision its Build list relies on.
   - Every step's **Depends on** points at earlier steps only.

## Reply

The plan path, the steps table, the open blockers with their owners, and the prompt that starts step 01.
