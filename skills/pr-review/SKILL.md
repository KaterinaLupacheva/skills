---
name: pr-review
description: Review a PR that is ready for review and end with VERDICT PASS or FAIL, plus the list of must-fix items when it fails. Runs unattended, so it fits a cloud routine.
disable-model-invocation: true
argument-hint: "[pr-number] [--no-post]"
---

# PR review

Decide whether one PR is ready to merge. Every finding is either **must-fix**, meaning it fails the PR, or **advisory**, meaning it never changes the verdict. A must-fix finding is **proven**: a failing check, a quoted spec line the diff misses, a run that shows wrong behavior, or a cited repo rule the diff breaks.

Run unattended. Nobody is there to answer questions, so resolve every gap yourself and name the assumption in the report.

Talk to GitHub only through `gh api` REST calls. Claude cloud sessions block GitHub GraphQL, which `gh pr` and `gh issue` use.

## 1. Pin the PR

- The PR is the number in `$ARGUMENTS`. Otherwise it is the open PR that contains `HEAD`, found with `gh api "repos/{owner}/{repo}/commits/$(git rev-parse HEAD)/pulls" --jq '.[] | select(.state == "open") | .number'`. This covers a run a PR event starts, which begins at the PR's head commit and may have no branch checked out. Otherwise it is the open PR for the current branch (`gh api 'repos/{owner}/{repo}/pulls?head={owner}:<branch>&state=open'`). With no PR at all, review the current branch against the default branch's merge base, and skip posting.
- Read it: `gh api 'repos/{owner}/{repo}/pulls/<n>'`. Its `base.ref` is `<base>` and its `head.sha` is `headRefOid` below.
- Review the PR's head commit without touching the user's checkout. Run `git fetch origin <base> pull/<n>/head`. If `HEAD` is already `headRefOid` and the tree is clean, review in place. Otherwise run `git worktree add --detach <scratchpad>/pr-<n> <headRefOid>` and work there, installing dependencies the way the repo's docs or lockfile say.
- A new worktree has no env file. Build one from the `.env.example` at `headRefOid`: take each variable it lists from the main checkout's `.env`, and for one the main `.env` lacks, take the non-secret value `.env.example` gives. The main checkout's `.env` follows today's code, so a copy of it can fail the PR's checks on variables the PR's code still needs.
- The diff is `git diff origin/<base>...<headRefOid>`, and the commit list is `git log --oneline origin/<base>..<headRefOid>`.

Done when the diff is non-empty and you hold the PR body, the diff command, and the review directory.

## 2. Gather the contract

Read the rule and validation files as they are at `headRefOid`, in the review directory. A rule added to the base branch after the PR's commit doesn't apply to it.

- **Spec**: every `#N` that the PR body or commit messages close (`Closes #N`, `Fixes #N`) or name as the work item. Read each one with `gh api 'repos/{owner}/{repo}/issues/<N>'` and its comments with `gh api 'repos/{owner}/{repo}/issues/<N>/comments' --paginate`. Its acceptance criteria are the spec. With no issue, the PR body's stated goal is the spec, and the report says so.
- **Rules**: `AGENTS.md`, `CLAUDE.md`, `CODING_STANDARDS.md`, `CONTRIBUTING.md`, and every doc they point to that covers the changed files.
- **Required validation**: the repo's table or list of checks each kind of change needs (in `teach` it is `docs/agents/change-protocol.md` §5). With none written, use the `package.json` scripts that typecheck, lint, and test.

Done when you can name the spec, the rule files, and the required checks for this diff's change types.

## 3. Run the checks

Run every required check that can run here, once, in the review directory. Record the command, the exit code, and the failing lines.

A check that needs something this session lacks, such as Docker, a running app, a live model, or the `verify-*` skill's setup, counts as **evidenced** when the PR body shows its result: the command and its output, or a written proof that names the screen or path it drove, what it saw before and after the change, and the value it read back. Screenshots stay in the session that took them, so a proof without them still counts when it gives those three. Record which checks were evidenced and which were neither run nor evidenced.

Done when every required check is **passed**, **failed**, **evidenced**, or **missing**.

## 4. Review in parallel

Spawn two `general-purpose` subagents in one message, foreground. Give each one the review directory, the diff command, the commit list, the check results from step 3, and its brief below. Each brief ends with: "Report under 400 words. For each finding give a title, `file:line`, the evidence, the fix, and whether you claim it is must-fix. No findings is a valid result."

- **Spec and rules** (`model: sonnet`). Pass the spec text and the rule files. "First, list each acceptance criterion the diff misses, covers only partly, or implements wrongly, quoting the criterion and the hunk. Then list each place the diff breaks a written rule, citing the file and the rule, and skip what the step 3 checks already enforce. List behavior the spec didn't ask for, and code smells, naming, and structure you would change, as advisory."
- **Bugs** (`model: opus`). Pass the PR's stated intent. "Break this change: wrong output, a crash, a regression in code that calls the changed code, stored data the new code can't read, a race. Prove each finding with a run against the real code: a failing test, a repro script, or command output. Put temporary test files in the review directory and delete them before you report. A finding you could only trace by reading counts when you give the concrete input, the path through the code, and why no run was possible here."

When the tool rejects a `model`, drop it, spawn again, and note this in the report.

Done when both reports are in.

## 5. Verify

Check every finding you will report yourself, advisory ones included:

- Re-read the cited lines at `headRefOid`, and correct the `file:line` when it is off. For an advisory finding, this check is enough.
- Rerun the repro command and compare its output with the report.
- Find the quoted criterion or rule in its source.

Keep a finding as must-fix when the evidence holds and it meets the verdict rule below. Move it to advisory when it holds but misses the rule. Drop it when the evidence doesn't hold, and count it under "Dropped" with the reason. Merge findings that share a root cause.

Done when every finding you report cites lines you re-read, and every must-fix finding carries evidence you confirmed yourself.

## Verdict rule

**FAIL** when any one of these holds; otherwise **PASS**:

1. A required check **failed** or is **missing**.
2. An acceptance criterion from a linked issue is missed, partly done, or done wrongly.
3. A proven bug or regression that breaks the spec or the PR's stated behavior on a path a real user can hit in normal use. Name that path in the finding. A bug that needs unusual timing or input to reach, or whose worst outcome is the behavior before the PR, is advisory, and its advisory line says so.
4. A broken written repo rule, including a weakened lint rule, test, or quality setting without the documented reason the rules ask for.

Everything else is advisory: smells, naming, extra scope that breaks nothing, a PR body with no linked issue that claims more than the diff does (rule 3 still fails behavior the body promises and the diff breaks), a risk that needs a future change to matter, and a check you'd add beyond what the rules require.

## 6. Report

Write the report in this shape. The first line is the verdict, so a reader or a script can find it.

```markdown
<!-- pr-review -->
**VERDICT: FAIL**

<One sentence: what the PR sets out to do and whether it does.>

## Must fix
1. **<title>** (`path/to/file.ts:42`). <What is wrong.> <Evidence: the failed command and its output, the quoted criterion, the repro output, or the cited rule.> **Fix:** <the change that resolves it.>

## Advisory
- <one line each, at most five, most useful first>

## Checks
| Check | Result |
| --- | --- |
| `pnpm check` | passed |
| verify-teach proof | missing: needed for a user-visible change, not in the PR body |

Reviewed `<short headRefOid>`. Spec: #<N>. Dropped: <count and reason, or "none">.
```

For **PASS**, write `None.` under "Must fix".

Post the report unless `$ARGUMENTS` has `--no-post` or step 1 found no PR. Find an earlier report with `gh api 'repos/{owner}/{repo}/issues/<n>/comments' --paginate --jq '.[] | select(.body | startswith("<!-- pr-review -->")) | .id'`. When one exists, update it with `gh api -X PATCH repos/{owner}/{repo}/issues/comments/<id> -F body=@<file>`. Otherwise run `gh api 'repos/{owner}/{repo}/issues/<n>/comments' -F body=@<file>`.

After posting, swap the PR's labels to the verdict. Remove `needs-review`, `review-pass`, and `review-fail` with `gh api -X DELETE 'repos/{owner}/{repo}/issues/<n>/labels/<label>'`, ignoring the 404 for a label the PR doesn't have. Then add `review-pass` or `review-fail` with `gh api 'repos/{owner}/{repo}/issues/<n>/labels' -f 'labels[]=<label>'`. Remove `needs-review` before adding the verdict. A scheduled task that fires on `needs-review` being labeled would otherwise see the verdict label as another matching event and start a new review. Skip the labels whenever you skip posting.

Then remove the worktree from step 1, if you made one.

End your reply with the verdict line, the must-fix titles, and the comment's URL.
