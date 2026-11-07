# Step NN. <Task as a verb phrase>

**Depends on.** <Earlier steps, or None. Blockers by name.>

**Goal.** <What is observably true after this step, and what does not use it yet.>

Read README decisions <D numbers> before you start.

## Files

- Create `<path>`.
- Edit `<path>`.

## Build

1. <One change. Name the symbol, the file, and the prior-art file to copy.>

## Tests

<The runner, and the existing test file whose mocking pattern to copy.>

`<test file>`:

- [ ] [agent] <Input or state, and the expected result.>

## Verify

- [ ] [agent] `<test command>` passes.
- [ ] [agent] `<typecheck command>` has no new errors.
- [ ] [user] <Action, and what the user sees. Save <evidence>.>

## Results

<Only for a step that measures or records something. One table row per value, filled in during the session.>

## Done when

Every box above is checked with its evidence. When the session runs clean-mode, its gates are clean too. Set this step's row in the README.
