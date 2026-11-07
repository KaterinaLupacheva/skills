# <Ticket> <Title>

<Under ten lines. What happens today, what changes after this work, for whom, and what stays the same.>

This folder is the implementation plan. Each step is one file and one session. Leave the work uncommitted unless <user> asks for a commit in that session.

## How to run a step

1. Open the step file. Start it only when every step in its **Depends on** is `done` and none of its blockers is open.
2. Read this README in full, then the decisions the step names.
3. Start the session with this prompt:

   ```
   Implement docs/plans/<slug>/<step file>. Read docs/plans/<slug>/README.md first.
   ```

4. Check a box only when its evidence exists: a passing command, a saved screenshot, a recorded value.
5. A decision made during the session gets the next D number, with the date and who made it. Update every step file it changes.
6. At the end of the session, update the step's row in the table below.

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

### D0. <The decision, as a statement>

<Date and who decided. The rule, the reason, and the `file:line` references. A decision table has one row per combination of input states.>

## Commands

<Typecheck, test and lint, as this repo runs them.>

## Repo rules

<The rules from CLAUDE.md that these steps touch.>
