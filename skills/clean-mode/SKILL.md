---
name: clean-mode
description: Uncle Bob's ub-mode for TypeScript. Plan before coding, then TDD, then the CRAP and duplication gates, plus the mutation gate for pure logic. Work stays uncommitted.
disable-model-invocation: true
---

# Clean mode

Adapted from [unclebob/ub-mode](https://github.com/unclebob/ub-mode). Once loaded, this mode governs the rest of the session until the user opts out. Re-read it after a compaction.

Every change runs four phases in order: **Before Coding**, **Make it Work**, **Make it Right**, **Report**.

## Principles

Each `###` heading below, and each bold name marked *(principle)*, is a principle with its full write-up at `../principle-<name>/SKILL.md`, the heading in kebab case (Attack the Premise → `../principle-attack-the-premise/SKILL.md`). TDD, Refactoring, Cleanup, and Gates have no write-up; Architecture has none either, but each of its bold names is a principle. Read a principle's file the first time you act on its rule in a session, and again when a gate fails twice on code it governs.

## No commits, no PRs

Leave the work uncommitted in the user's working tree and end with the verified diff. Commit, push, or open a PR only when the user asks for it in this session.

## Subagents

You stay on the session model and own the judgment: all of Before Coding, every Attack the Premise and Architecture call, the review of each delegate's diff, Prove It Works, Explain the Number, and the Report. Delegates do the volume.

Spawn each delegate with the `Agent` tool, `subagent_type: "general-purpose"`, and an explicit `model`:

| Work | Model |
|---|---|
| One Make it Work unit: its failing test, the smallest passing change, its check | `sonnet`; `opus` for cross-cutting design, concurrency, or subtle algorithms |
| A gate fix | the model of the unit that owns the function |
| Running the baseline or the gates, returning the filtered output | `haiku` |
| Bulk read-only exploration | `haiku` |

- When `${CLAUDE_CONFIG_DIR:-~/.claude}/pstack-models.md` exists, its role lines override the unit models: `bug-fix` for a bug unit, `feature, refactoring` for the rest, `hardest tasks` for the `opus` cases. A value of `inherit-parent` or `auto` means omit `model`.
- If the tool rejects a model, omit `model` so the delegate runs on the session model, and say so in the log.
- Give every unit and every fix round a fresh delegate.
- Run units one at a time, in plan order, in the shared working tree. Review each unit's diff and see its check pass before the next unit starts. The mutation gate rewrites source in place, so a gate runner works alone.
- Each brief carries this file's absolute path, the one unit the delegate owns (Before Coding is done), the unit's check, the TDD rules, the baseline violations to leave alone, and the No commits rule. A delegate cannot ask you anything, so the brief settles every choice, and any product question comes back to you unanswered.
- A gate runner reports violations. A code delegate or you fixes them.
- Do a trivial unit (a rename, a one-line change) yourself.

## 1. Before Coding

When the task is one step of a step plan, the step file is your plan. Its Verify boxes are the acceptance check, its Build list gives the units, and its decisions are settled. Go straight to step 5.

1. Name the change: **bug**, **feature**, or **refactor**.
2. Write the **acceptance check**: the observable result that proves the change is done, such as a test that goes red now and green after, or a command and its expected output.
3. Close the open questions:
   - Bug: reproduce it as a failing test. If the cause is still unclear once it reproduces, run `/diagnosing-bugs`.
   - Feature with a gap in the requirements (an unstated edge case, unclear input or output, two readings of one behavior): run `/grill-with-docs` until every gap has an answer. It loads the `grilling` and `domain-modeling` skills. If you can't run it, load those two directly.
   - Work that needs more than one session, or waits on something you cannot do (a credential, test data, a check only the user can run): write a plan with the `step-plan` skill and stop. Each later session implements one step.
   - New domain term: record it in the glossary with `/domain-modeling`.
   - UI change (an existing screen, or a new component): ask the user whether to run `/prototype` first, and wait for the answer. On yes, the prototype's answer feeds the plan. When the interaction has no precedent in the codebase, the prototype builds 2–3 competing variants side by side (**Exhaust the Design Space** *(principle)*).
4. Plan the work as an ordered list of verifiable units, each with its own check.
5. Take the **baseline**: run the gates that apply (see **Gates**) on the files the plan touches, by path instead of `--changed`. Note every violation that already exists, so you can tell yours apart later.

Done when your reply states the change type, the acceptance check, the unit list, the baseline, and zero open questions.

## 2. Make it Work

### Never Block on the Human

- Before Coding is where you ask. From here on, make each reversible choice yourself, then name it in the log.
- Product direction and irreversible actions still go to the user.

### Experience First

- When implementation convenience conflicts with what the user of the work experiences, choose the experience. For a library, that user is the caller.

### Laziness Protocol

- One decision lives in one place.
- Ship the smallest edit that solves the problem.

### Foundational Thinking

- Get the data shape right before you write the logic.
- Do first whatever helps every later phase.
- If a concurrent writer would matter, give each writer its own state.

### TDD

- Write the failing test before you change the code.
- See it fail for the reason you expect.
- Make the smallest change that makes it pass.
- If an honest test is impractical, say so and skip it rather than write a bad one.

### Redesign From First Principles

- Build what you would have built if the new requirement had been there from the start, and deliver it in pieces.

### Attack the Premise

- When two fixes that share one premise fail the same gate, write that premise in one sentence and count which actors hold the imbalance.
- Remove that assignment before you start another fix.

### Subtract Before You Add

- Take complexity out before you add anything.

### Outcome-Oriented Execution

- Aim at the end state you can check.
- A break in the middle is allowed when you planned it and can undo it.

### Build the Lever

- If the work is not obvious at a glance, build the tool that does it.
- Do one unit by hand, then make the tool match that unit.

### Architecture

- **Model the Domain**: shape the types so illegal states cannot be built. If the code is already clear and local, leave it.
- **Boundary Discipline**: check data where it enters, trust it inside, and keep business logic in pure functions.
- **Type System Discipline**: parse outside data once, at the boundary, and fix every type error at its source. `/typescript-best-practices` has the TypeScript rules.
- **Make Operations Idempotent**: running it twice, or after a crash halfway through, ends in the same state.
- **Separate Before Serializing Shared State**: if they need different mutable things, give each its own. If they share one, allow a single writer and enforce that in the structure.
- **Migrate Callers Then Delete Legacy APIs**: when a new internal API replaces an old one, move every caller and delete the old API in the same change. Keep a compatibility layer only for external users.

## 3. Make it Right

### Fix Root Causes

- Reproduce it, then fix the cause. A guard that only hides the crash is not a fix.

### Sequence Verifiable Units

- Finish one small unit and check it, then start the next.

### Test Behavior, Not Implementation

- The test calls the code the way its user does and checks what that user would see.
- If the test would still pass when every function returned nothing, throw it out.

### Refactoring

- Pin what the code does, change the structure, then prove the behavior did not change.

### Minimize Reader Load

- Inline wrappers with one caller and layers that pass the same arguments through.
- Shrink state scope: returns over mutations, locals over fields, fields over module state.

### Encode Lessons in Structure

- When you give the same correction a second time, encode it as a lint, type, test, or script instead of another instruction.

### Cleanup

After the last unit passes, before the gates:

1. Run `/no-comments` on the diff.
2. Run `/unslop` on the prose the diff adds or changes: Markdown, docs, glossary entries, user-facing strings.

### Gates

Run from the project root, after the project's full typecheck and test scripts pass. Run the whole test script, not only the tests of the files you touched: a changed id, type or shared fixture breaks tests in other files. `TOOLS` is the `tools/` folder next to this file. The gates cover every function you added or edited. Violations from the baseline in functions you left alone go into the report, unfixed.

1. **CRAP**: every function scores below 10.
   ```bash
   "$TOOLS/run.sh" crapper --changed 2>&1 | sed -n '/CRAP Report/,$p'
   ```
   Fix by splitting the function, by testing it, or both. A flat `switch` that maps values may be worth keeping as it is, so weigh the split.
2. **Duplication**: no `DUPLICATE` pair includes your code. dryer exits 0 even when it finds pairs, so read the output.
   ```bash
   "$TOOLS/run.sh" dryer --changed --threshold 0.8
   ```
3. **Mutation**, for pure logic only: no `SURVIVED` or `UNCOVERED` line falls in your functions. Exit 3 means a mutant survived.
   - Run it on `.ts` files with no JSX (utilities, domain functions, reducers, selectors) whose tests run in Node or jsdom. Pass those files by path and narrow the suite to their unit tests:
     ```bash
     "$TOOLS/run.sh" mutator <files> --test-command "<unit test command for those files>" 2>&1 | grep -E '^(SURVIVED|UNCOVERED)|Score|Total'
     ```
   - Skip it for components (`.tsx`) and for any file that only browser tests cover (Storybook, Playwright). Name the skipped files in the report. Its operators (`===`, `&&`, `??`, booleans, constants) miss the bugs that live there: layout, event handling, async order. Coverage can't see browser tests, so their lines show as `UNCOVERED`, and each mutant reruns a slow browser suite.
   - For `UNCOVERED`, add a test that runs that line, or delete the line if nothing needs it. Ignore `UNCOVERED` lines inside test files and test helpers. For `SURVIVED`, write a test that fails under that mutant. A survivor that no input can tell apart from the original (such as `??` → `||` on a value that is never `0`, `''` or `false`) is an equivalent mutant: name it in the report and leave it.

Each fix changes code, so rerun the gates that apply. Done when a single pass of them is clean.

### Prove It Works

- Run the acceptance check against the real artifact: run the feature, read the actual value, inspect the diff. A passing compile or a subagent's report is a proxy.

### Explain the Number

- When the task reports a measured number (a speedup, a latency, a size), name what bounds it and rule out that it measured something else, such as skipped work, a cache, or noise. Keep the run count and spread with the number.

Tool facts the output won't tell you:

- `--changed` reads `git status`, so it includes untracked files. It reports every function in a touched file, which is why the baseline matters.
- The tools write `.metrics/` and `target/` into the project. If the project doesn't ignore them, add both to `.git/info/exclude` so they stay out of the diff.
- crapper collects coverage itself. In a Vitest project it installs `@vitest/coverage-v8` without saving it, and restores `package.json` afterwards. Other test runners are wrapped in `c8`, and a `coverage` script is used as it is.
- crapper merges every `target/coverage/**/lcov.info` and `coverage/**/lcov.info`, and the last report read wins. An old, git-ignored `coverage/lcov.info` makes a tested file show 0%: move it aside for the run, then put it back.
- Coverage sees only Node and jsdom tests. A function that only browser tests run (Storybook, Playwright) shows 0%, so its CRAP is CC² + CC. In a Vitest workspace with a browser project, pass `--coverage-command` that runs only the unit project. For a story-only function, report its complexity and the stories that cover it instead of a failing score.
- mutator runs `npm test` from the nearest `package.json`. Pass `--test-command "<cmd>"` to run a narrower suite. Later runs only retest survivors and functions whose text changed.
- mutator rewrites source files in place while it runs. Make no edits until it finishes. A dev server or Storybook with hot reload sees every rewrite and can stop responding, so stop it first or restart it after. Parallel workers each run the test command, so a large suite can exhaust memory: keep the suite narrow or pass `--max-workers`.
- The first run of each tool builds its Python virtualenv. `run.sh` picks Python 3.11 or newer.

## 4. Report

- **Log**: keep a log of every action and the reason for it, as you go.
- **Context window** (**Guard the Context Window** *(principle)*): keep the main thread small. Filter tool output as the gate commands do, send bulk exploration to subagents, and keep their summaries.

The final reply contains:

- the acceptance check and its result
- the gate results, as the worst CRAP score, the duplicate pairs, and killed/survived/uncovered counts (or the files the mutation gate skipped, and why)
- what `/no-comments` and `/unslop` changed
- baseline violations left in place
- the log
- the changed files
