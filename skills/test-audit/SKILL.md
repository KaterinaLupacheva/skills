---
name: test-audit
description: Read-only audit of a test suite for tests that can't catch a bug. Reports orphan imports, assertions that may never run, assertions that can't fail, and flaky inputs.
disable-model-invocation: true
argument-hint: "[path]"
---

# Test audit

Find tests that pass whether or not the code works. Read the tests and report **candidates**, each with the line that proves it. Running the suite, editing files, and judging coverage numbers belong to other work, so this audit only reads.

Scope is `$ARGUMENTS` when given, otherwise the whole repo.

## Signals

Ranked by severity, highest first.

1. **Orphan.** A test imports a module, file, or symbol that no longer exists in the source tree. The test either fails to load or tests a stub. Resolve each relative import and path alias against the tree, and check that each named import is still exported.
2. **Silent.** An assertion that can be skipped while the test still passes:
   - inside an `if`, a `catch`, or a loop over a collection that can be empty
   - in a callback or promise the test doesn't `await` or return
   - an expected-throw test with no `expect.assertions(n)`, `pytest.raises`, or equivalent guard
   - a test body with no assertion at all
3. **Hollow.** An assertion that can't fail: `expect(true).toBe(true)`, `assert True`, `expect(x)` with no matcher, `toBeDefined()` on a value the test just built, a mock asserted against the value it was told to return, or a snapshot of a constant.
4. **Flaky.** The result depends on something outside the test: real time (`Date.now`, `new Date()`, `datetime.now`), randomness with no seed, `sleep` or fixed timeouts, real network or filesystem, order of an unordered collection, or state shared between tests with no reset.

## Steps

1. **Find the tests.** List test files with `git ls-files` filtered by the repo's test naming (`*.test.*`, `*.spec.*`, `test_*.py`, `*_test.go`, and the test config's `include` patterns). With more than 300 files, audit the 300 most recently changed and say so in the report.
2. **Sweep.** Grep for each signal's patterns across the files. Grep is line-based, so treat a hit as a lead and read the surrounding test to confirm it.
3. **Confirm.** Every candidate in the report has been read in context and cites `file:line`. Drop hits that are intentional, such as a loop over a fixed non-empty table of cases.
4. **Report.** Group by signal in severity order, at most 15 findings, then one line with the count per signal including any beyond the 15. Format each finding as:

   `path/to/file.test.ts:42 — Silent: expect inside .forEach over results (passes when results is empty)`

   End with the one finding most worth fixing first and why.
