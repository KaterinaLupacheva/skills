---
name: update-pstack
description: "Update this repo's pstack skills to the latest cursor/plugins upstream and re-apply the Claude Code port. Use for /update-pstack, \"update pstack\", or \"sync pstack\"."
disable-model-invocation: true
metadata:
  internal: true
---

# Update pstack

Run from the repo root. `PORTING.md` is the authority for every Cursor to Claude Code mapping. Read it in full before step 4.

1. Require a clean tree (`git status --short` prints nothing), then `git pull`. Stop and report if either fails.
2. `./update-pstack.sh`. It overwrites every pstack file with raw upstream.
3. `./merge-upstream.sh pstack`. It three-way merges each overwritten file with HEAD's ported copy and prints:
   - `CONFLICT` files, with `<<<<<<< local` / `>>>>>>> upstream@<new>` markers where upstream changed lines the port also changed.
   - `NEW` files, which arrive as raw upstream.
   - `REMOVED` files, which upstream deleted.
   - `AGENTS`, when upstream's agents changed. `agents-upstream/` holds the new copies.
4. Port by hand, using `PORTING.md`:
   - Resolve each conflict to upstream's new content with the port's mappings applied. Keep upstream's change. Do not just pick the `local` side.
   - Port each `NEW` file. A new skill also gets a row in `poteto-help`'s table if upstream added one there.
   - For each `REMOVED` file, find what still links to it with `grep -rn <filename> skills agents` and fix those links.
   - Apply `AGENTS` changes to `agents/`, then `rm -rf agents-upstream`.
   - A Cursor-ism with no mapping in `PORTING.md` gets one added there. Pick the port, apply it, and add the row.
5. `.claude/skills/update-pstack/check-port.sh` until it prints `Port check passed.` A pattern it lacks for a mapping you just applied goes into its `patterns` list.
6. Show the user `git diff --stat` plus the list of conflicts, new files, and judgment calls from step 4. Commit with `git commit -m "Update pstack to upstream $(cut -c1-7 PSTACK_UPSTREAM)"`. Push only when asked.
