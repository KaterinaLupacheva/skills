---
name: resolve-merge-conflicts
description: "Resolve an in-progress git merge, rebase, cherry-pick, or stash-pop conflict. Reads why each side changed, and inspects conflict hunks instead of whole files. Use when git stops on conflicts, `git status` shows unmerged paths, or files contain conflict markers."
metadata:
  credits:
    - skill: resolve-merge-conflicts
      author: Warp
      url: "https://github.com/warpdotdev/common-skills/tree/main/.agents/skills/resolve-merge-conflicts"
    - skill: resolving-merge-conflicts
      author: Matt Pocock
      url: "https://github.com/mattpocock/skills"
---

# Resolve merge conflicts

Let `SKILL_ROOT` be the directory holding this file. `ctx` below stands for `python3 "$SKILL_ROOT/scripts/extract_conflict_context.py"`. Use it before opening any conflicted file.

1. **See the state.** Run `ctx`. It lists the unresolved paths, their index stages, and the hunk count per file. Note which operation stopped (merge, rebase, cherry-pick, stash pop) and what it is meant to achieve.
2. **Learn why each side changed.** For each conflicted file, read the commits that touched it on both sides, then the PRs and issues they link. Know what each side intended before you touch a hunk.
3. **Resolve one file at a time.** Run `ctx --file <path>`. It prints ours, base, and theirs for each hunk with nearby context, plus a compact diff between ours and theirs. Read more of the file only when that isn't enough.
   - Keep both intents where they fit together. Where they don't, keep the side that matches the operation's goal and note the trade-off. Don't invent new behavior.
   - Take a whole side with `git checkout --ours -- <path>` or `--theirs` only when the other side's intent is fully superseded. During a rebase, `ours` is the branch you are rebasing onto and `theirs` is your commit.
   - Add/add and modify/delete conflicts have no markers. `ctx --file` shows their index stages instead.
4. **Confirm nothing is left.** `ctx` and `git diff --name-only --diff-filter=U` both come back empty, and `git grep -nE '^(<<<<<<<|=======|>>>>>>>)( |$)' -- <resolved paths>` finds no markers.
5. **Run the project's checks.** Typecheck, then tests, then format. Fix whatever the merge broke.
6. **Finish the operation.** Stage the resolved files and run `git merge --continue`, `git rebase --continue` until every commit applies, or `git cherry-pick --continue`. Never abort.

`ctx` also takes `--all` for every file in detail, `--json`, `--context N` (default 2), and `--max-lines N` per section (default 40).
