# <Ticket> <Title>

<Under ten lines. What happens today, what changes after this work, for whom, and what stays the same.>

This folder is the implementation plan. Each step is one file and one session. Leave the work uncommitted unless <user> asks for a commit in that session.

## How to run a step

1. Open the step file. Start it only when every step in its **Depends on** is `done` and none of its blockers is open.
2. Read this README in full. Then print only the decisions the step names, never all of `decisions.md`. For example, for D1 and D5:

   ```
   awk '/^### D[0-9]/{p=0} /^### D(1|5)\./{p=1} p' docs/plans/<slug>/decisions.md
   ```

3. Start the session with this prompt:

   ```
   Implement docs/plans/<slug>/<step file>. Read docs/plans/<slug>/README.md first.
   ```

4. Check a box only when its evidence exists: a passing command, a saved screenshot, a recorded value.
5. A decision made during the session gets the next D number in `decisions.md`, with the date and who made it, and a row in the **Decisions** index below. Update every step file it changes.
6. At the end of the session, update the step's row in the table below. Results and notes go in the step file, not here. Keep this README under 6 KB.
7. End your final reply with the prompt for the next session: the first step in the table that is not `done`, in the prompt format above, in a code block. If that step is `blocked`, name the blocker instead. If every step is `done`, say the plan is complete.

## Steps

| Step | File | Depends on | Status | Open boxes |
|---|---|---|---|---|
| 01 | [01-<slug>.md](01-<slug>.md) | None | todo | <n> |

Status is `todo`, `in progress`, `blocked` or `done`. A `blocked` step has its blocker in **Blockers**.

## Blockers

| Blocker | Needed by | Owner | State |
|---|---|---|---|
| <What the agent cannot do or fetch itself> | <Step NN> | <who> | open |

## Box tags

- `[agent]`: the agent runs it and records the evidence.
- `[user]`: <user> runs it, because it needs a person, a real account, or a browser the agent cannot drive.
- `[needs: X]`: it waits on blocker X.

## Safety rules

<Which data is real, which calls change state, and the one step allowed to make them.>

## Decisions

Full text in [decisions.md](decisions.md). One line each.

| D | Decision | Used by |
|---|---|---|
| D0 | <The decision, as a statement> | <Step NN> |

## Commands

<Typecheck, test and lint, as this repo runs them.>

## Repo rules

<The rules from CLAUDE.md that these steps touch.>
