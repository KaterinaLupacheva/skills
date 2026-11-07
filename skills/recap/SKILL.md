---
name: recap
description: "Short recap of what changed in a project over the last N days: features, files, structure, database. Use for /recap [days] [path]."
argument-hint: "[days, default 7] [project path, default cwd]"
disable-model-invocation: true
---

# Recap

Tell the user what changed in a project over the last N days, as a recap they read in under a minute. Arguments: days (default 7) and a project path (default the working directory). Work read-only.

## 1. Gather

Run every command from the project root with `git -C <path>`. Use the default branch (`main` or `master`) as the record; mention unmerged branches with commits in the window in one line at the end.

- Commits: `git log --since="<N> days ago" --no-merges --format='%h %ad %s' --date=short`. No commits means reply with one line saying so, and stop.
- Base: the parent of the oldest commit in the window. Diff stats: `git diff --stat --find-renames <base> HEAD` and `git diff --name-status --find-renames <base> HEAD`.
- PRs, when `gh` works in this repo: `gh pr list --state merged --search "merged:>=<date>" --json number,title`. PR titles beat commit subjects when grouping.
- Database: the changed paths that match a schema signal: `migrations/`, `supabase/`, `prisma/schema.prisma`, `schema.rb`, `*.sql`, `models.py`, Drizzle/TypeORM/Sequelize schema files, or whatever the project's `AGENTS.md`/`CLAUDE.md` names. Read the diffs of the migration files themselves; they are the truth about tables, columns, indexes, policies and functions.
- Structure: top-level and second-level directories that were added or deleted (`--name-status` `A`/`D` rows grouped by their first two path segments).

Gathering is done when every commit in the window belongs to exactly one feature group (step 2) and every migration file in the window has been read.

## 2. Group

Fold commits into **features**: user-visible capabilities, named in product language, one line each. Conventional-commit scopes and issue numbers are hints, not the grouping. Fixes, chores, CI, docs and tests that serve a feature join it; the rest form one "Maintenance" line at most.

## 3. Write

The whole reply fits one screen. Use this shape, dropping any section with nothing in it:

```
**<project> · last <N> days** · <commits> commits · <PRs> PRs · +<added>/−<deleted> lines

**Features**
| Feature | What it does | Refs |
|---|---|---|
(≤ 8 rows, most significant first; merge the tail into "Smaller: …")

**Where the code changed**
| Area | Files | Notes |
|---|---|---|
(≤ 6 rows, areas from the top two path segments, ordered by lines of code changed; binary assets such as images and fonts rank last and get one mention in Notes)

**Database**
- one bullet per migration: what it adds or changes, in table.column terms

**Structure**
- new or removed modules/directories, one bullet each

**Maintenance** one line: tooling, CI, deps, docs.
```

Tables carry the features and areas because they scan fastest. Add a diagram only when the window changed the shape of something, drawn as plain text so it renders in a terminal: one `new_table → parent_table (1:1)` line per new relation under Database, or a short tree of new directories under Structure. A window with only column tweaks or file edits gets no diagram.

Every claim comes from a commit, a diff or a migration you read. When a line would need guessing, leave it out.
