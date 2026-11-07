---
name: update-mattpocock
description: "Update this repo's copy of Matt Pocock's skills to the latest mattpocock/skills upstream, keeping local edits. Use for /update-mattpocock, \"update matt pocock skills\", or \"sync matt's skills\"."
disable-model-invocation: true
metadata:
  internal: true
---

# Update Matt Pocock's skills

Run from the repo root.

1. Require a clean tree (`git status --short` prints nothing), then `git pull`. Stop and report if either fails.
2. `./update-mattpocock.sh`. It overwrites every skill in upstream's `.claude-plugin/plugin.json` list with raw upstream.
3. `./merge-upstream.sh mattpocock`. It three-way merges each overwritten file with HEAD's copy, so local edits survive where upstream left those lines alone. It prints:
   - `CONFLICT` files, with `<<<<<<< local` / `>>>>>>> upstream@<new>` markers where upstream and a local edit changed the same lines.
   - A `CONFLICT` marked "not from mattpocock before this update" means a new upstream skill overwrote one of mine or a pstack skill. Restore it with `git restore <dir>`, then ask the user which skill gets renamed.
   - `NEW` files and skills, which arrive as raw upstream.
   - `REMOVED` files, which upstream deleted.
   - `DROPPED` skills, which upstream no longer lists. The script leaves them in place.
4. Resolve each conflict so both upstream's change and the local edit's intent survive. When they contradict, keep the local edit and list it for the user. For each `REMOVED` file, fix whatever still links to it (`grep -rn <filename> skills`).
5. `.claude/skills/update-pstack/check-port.sh`. It also fails on leftover conflict markers and on a skill whose `name` doesn't match its directory. Fix until it prints `Port check passed.`
6. Show the user `git diff --stat`, the conflicts and how each was resolved, new skills, and `DROPPED` skills to decide on. Commit with `git commit -m "Update Matt Pocock's skills to upstream $(cut -c1-7 MATTPOCOCK_UPSTREAM)"`. Push only when asked.
