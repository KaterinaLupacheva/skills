# Claude Code skills

A collection of skills for [Claude Code](https://claude.com/claude-code). It bundles two outside skill sets, two skills adapted from Warp, and a few skills of my own:

- **pstack** by Lauren Tan, ported from Cursor to Claude Code. Upstream is [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack). It is an agent working style built on `/poteto-mode`, with parallel subagents, adversarial review, verified work, and 24 engineering principles.
- **Matt Pocock's skills** from [mattpocock/skills](https://github.com/mattpocock/skills). They cover planning, specs, tickets, TDD, and code review.
- **Two skills from Warp's** [common-skills](https://github.com/warpdotdev/common-skills/tree/main/.agents/skills), adapted for Claude Code. `/skill-doctor` grades your skills from your conversation history. `resolve-merge-conflicts` adds Matt Pocock's intent-first conflict steps.
- **My own skills.** `/clean-mode` adapts Uncle Bob's [ub-mode](https://github.com/unclebob/ub-mode) to TypeScript. `/step-plan`, `/recap`, and `rtl-check` are smaller helpers.

Each upstream set is pulled in with a script, and the Claude Code port of pstack is described in [PORTING.md](PORTING.md).

## Install

You need Claude Code. `/clean-mode` also needs Python 3.11 or later.

### Install with npx

Install with the [skills CLI](https://github.com/vercel-labs/skills), which works with Claude Code, Cursor, Codex, and other agents:

```bash
npx skills add KaterinaLupacheva/skills
```

The CLI asks which skills to install and for which coding tools. It installs into the current project by default. Add `-g` to install for every project, and `-a claude-code` to install for Claude Code without asking.

To install specific skills:

```bash
npx skills add KaterinaLupacheva/skills --skill clean-mode step-plan
```

To update later, run `npx skills update`.

The CLI installs skills only. pstack also uses two subagents, `poteto-agent` and `comment-sicko`. To install them for every project:

```bash
mkdir -p ~/.claude/agents
for agent in poteto-agent comment-sicko; do
	curl -fsSL "https://raw.githubusercontent.com/KaterinaLupacheva/skills/main/agents/$agent.md" -o ~/.claude/agents/$agent.md
done
```

Without them, pstack still works but uses generic subagents.

### Install from a clone

Use this to get updates with `git pull`, or to install the skills and agents in one step. You need `git`.

1. Clone the repo:

   ```bash
   git clone https://github.com/KaterinaLupacheva/skills.git ~/claude-skills
   ```

2. Link every skill and agent into your Claude Code config directory. A skill or agent with the same name as one you already have is skipped and listed, so the loop never overwrites your files.

   ```bash
   REPO=~/claude-skills
   CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
   mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents"
   for src in "$REPO"/skills/*/ "$REPO"/agents/*.md; do
   	src="${src%/}"
   	kind=$(basename "$(dirname "$src")")
   	dest="$CLAUDE_DIR/$kind/$(basename "$src")"
   	if [ -e "$dest" ] || [ -L "$dest" ]; then
   		echo "skipped, already exists: $dest"
   	else
   		ln -s "$src" "$dest"
   	fi
   done
   ```

3. Start a new Claude Code session and type `/poteto-help`. The skill autocompletes when the install worked. Run `/agents` and check that `poteto-agent` and `comment-sicko` are listed.

To update, run `git pull` in the clone. The links point at the clone, so the next session picks up the changes. To uninstall, delete the links. `rm` on a link never touches the clone.

### Install some of the skills

To install one skill, use `--skill` with npx, or link or copy its folder from `skills/` into `~/.claude/skills/`. To make a skill available in one project only, put it in that project's `.claude/skills/` instead.

Some skills only work alongside others:

- **pstack skills** read each other by relative path, so install them as a set: every skill listed under [pstack](#pstack) and [pstack principles](#pstack-principles), plus both files in `agents/`. Without the agents, pstack falls back to generic subagents.
- **`/clean-mode`** uses `/step-plan` for work that spans sessions, and runs the tools in `skills/clean-mode/tools/`.
- **Matt Pocock's skills** expect `/setup-matt-pocock-skills` to run once per project. If you want only his skills, install his plugin from [mattpocock/skills](https://github.com/mattpocock/skills) instead.

## Use a skill

Type `/` and the skill name in a Claude Code session, for example `/recap 14`. Text after the name is passed to the skill as arguments.

Most skills start only when you type their name. The tables mark the others with **Auto**. Claude loads those on its own when your request matches the skill's description.

Good first steps:

- `/poteto-help` explains pstack and picks the skill, playbook, or principle for a task.
- `/ask-matt` does the same for Matt Pocock's skills.
- `/setup-pstack` sets the model pstack uses for each subagent role. It writes `~/.claude/pstack-models.md`. Without that file, pstack uses its defaults.

## Skills

### My own

| Skill | What it does |
| --- | --- |
| `/clean-mode` | Works the way Uncle Bob's ub-mode does, for TypeScript. It plans before coding, then runs TDD, then the CRAP, duplication, and mutation gates. Work stays uncommitted. The gates use [crapper](https://github.com/unclebob/crapper), [dryer](https://github.com/unclebob/dryer), and [mutator](https://github.com/unclebob/mutator), which build their Python environment on first run. |
| `/step-plan` (Auto) | Writes an implementation plan as a folder in `docs/plans/<slug>/`. A README holds the numbered decisions, and each session-sized step gets its own file with tagged checkboxes. The folder stays out of git through `.git/info/exclude`. |
| `/recap [days] [path]` | Summarizes what changed in a git project over the last N days: features, changed areas, database, and structure. The defaults are 7 days and the current directory. |
| `/rtl-check` (Auto) | Finds directional CSS properties such as `margin-left` that have no RTL handling, and suggests logical-property fixes. |

### pstack

| Skill | What it does |
| --- | --- |
| `/poteto-mode` | Sets the agent style for the session: concise replies, deliberate subagents, plain prose, simple code, and verified work. It routes each task to a playbook. |
| `/poteto-help` | Guides you through pstack setup and picks the skill, playbook, or principle for a task. |
| `/setup-pstack` (Auto) | Sets the model pstack uses for each role. |
| `/how` | Explains how code works: architecture, runtime flow, and where something should live. |
| `/why` | Explains why code works the way it does, with citations from source control, trackers, docs, and chat. |
| `/pstack-teach` | Combines `/how` and `/why` into one plain explanation of a body of work. |
| `/architect` | Sketches types, signatures, and module structure before code, then stays in the loop during implementation. |
| `/arena` | Runs N candidates at one task, picks a base, and grafts the best parts of the others into it. |
| `/swarm` | Fans out N parallel workers and returns one report. |
| `/interrogate` | Runs adversarial review of a change or design. Only findings proven by a run survive. |
| `/blast-radius` | Finds what a change could break outside the diff, and proves the key safety fact by running code. |
| `/figure-it-out` | Designs an auditable playbook for a large or unattended task that no other playbook fits. |
| `/show-me-your-work` | Keeps a decision log for long or unattended runs, one row per decision. |
| `/benchmark-checklist` | Vets a performance measurement before you report or act on it. |
| `/statechart` | Checks a TLA+ model of a stateful system and draws it as a Mermaid statechart. |
| `/correct` | Finds mistakes agents keep repeating in a repo and makes each one impossible with structure, types, lints, or tests. |
| `/reflect` | Reviews the current transcript with three subagents and turns the lessons into edits to existing skills. |
| `/recall` | Rebuilds your recent working context from chat history and live state. |
| `/ketchup` | Catches you up on what changed in the chat since your last message. |
| `/ketchup-video` | Does the same as `/ketchup`, as a short subtitled slide video. |
| `/bro` | Restates the last message in plain language. |
| `/in-your-own-words` | Restates the user's goal and the problem behind it. |
| `/sharpen` | Makes a task deeper rather than bigger, then rewrites the prompt. |
| `/automate-me` | Drafts or updates a personal `-mode` skill from your working style. |
| `/pstack-tdd` | Runs test-driven development when you ask for it or when a cheap local test exists. |
| `/create-verification-skill` | Generates a project skill that drives your app the way a user does. |
| `/maintain-verification-skill` | Audits that verification skill against the code. |
| `/create-formal-verification-skill` | Generates a project skill that formally verifies the riskiest code. |
| `/maintain-formal-verification-skill` | Brings formal verification back in line after the code changes. |
| `/technical-writing` | Applies a layered standard to docs, readmes, PR descriptions, and commit messages. |
| `/unslop` (Auto) | Removes AI writing patterns from any text. |
| `/no-comments` (Auto) | Spawns the `comment-sicko` agent to remove comments that don't explain a non-obvious why. |
| `/typescript-best-practices` (Auto) | Applies TypeScript practices when Claude reads or edits `.ts` or `.tsx` files. |

### pstack principles

`/poteto-mode` loads these 24 skills when a task calls for them. You can also run one by name.

| Group | Skills |
| --- | --- |
| Core | `principle-laziness-protocol`, `principle-foundational-thinking`, `principle-redesign-from-first-principles`, `principle-attack-the-premise`, `principle-subtract-before-you-add`, `principle-minimize-reader-load`, `principle-outcome-oriented-execution`, `principle-experience-first`, `principle-exhaust-the-design-space`, `principle-build-the-lever` |
| Architecture | `principle-model-the-domain`, `principle-boundary-discipline`, `principle-type-system-discipline`, `principle-make-operations-idempotent`, `principle-migrate-callers-then-delete-legacy-apis`, `principle-separate-before-serializing-shared-state` |
| Verification | `principle-prove-it-works`, `principle-fix-root-causes`, `principle-sequence-verifiable-units`, `principle-test-behavior-not-implementation`, `principle-explain-the-number` |
| Delegation | `principle-guard-the-context-window`, `principle-never-block-on-the-human` |
| Meta | `principle-encode-lessons-in-structure` |

### Matt Pocock

| Skill | What it does |
| --- | --- |
| `/ask-matt` | Tells you which of these skills fits your situation. |
| `/setup-matt-pocock-skills` | Sets up a project's issue tracker, triage labels, and doc layout. Run it once per project. |
| `/grill-me` | Interviews you to sharpen a plan or design. |
| `/grill-with-docs` | Interviews you and writes ADRs and a glossary as it goes. |
| `/grilling` (Auto) | Stress-tests a plan, decision, or idea with hard questions. |
| `/to-spec` | Turns the conversation into a spec on the issue tracker. |
| `/to-tickets` | Breaks a plan or spec into tracer-bullet tickets with blocking links. |
| `/to-questionnaire` | Turns a decision you can't answer alone into a questionnaire for someone else. |
| `/wayfinder` | Plans work too big for one session as a map of decision tickets. |
| `/implement` | Implements work from a spec or a set of tickets. |
| `/implement-spec` | Implements the output of `/to-spec` and `/to-tickets`. |
| `/tdd` (Auto) | Runs red-green-refactor test-driven development. |
| `/diagnosing-bugs` (Auto) | Runs a diagnosis loop for hard bugs and performance regressions. |
| `/code-review` (Auto) | Reviews changes since a commit or branch against the repo's standards and the originating spec. |
| `/codebase-design` (Auto) | Gives a shared vocabulary for designing deep modules and choosing seams. |
| `/improve-codebase-architecture` | Finds deepening opportunities, shows them as an HTML report, and grills you on the one you pick. |
| `/domain-modeling` (Auto) | Builds a project's domain model, glossary, and ADRs. |
| `/prototype` (Auto) | Builds a throwaway prototype to answer a design question. |
| `/research` (Auto) | Researches a question against primary sources and saves the findings as Markdown in the repo. |
| `/triage` | Moves issues and external PRs through triage states and writes agent-ready briefs. |
| `/pr` (Auto) | Writes a PR body. |
| `/wizard` (Auto) | Generates an interactive bash script for setup steps only a human can do. |
| `/writing-for-agents` (Auto) | Guides writing skills, `AGENTS.md`, and `CLAUDE.md`. |
| `/handoff` | Compacts the conversation into a handoff document for another agent. |
| `/retro` | Runs a retrospective on a coding session. |
| `/teach` | Teaches you a skill or concept inside the workspace. |
| `/wait-what` | Re-pitches a message that didn't land. |

### Warp

| Skill | What it does |
| --- | --- |
| `/skill-doctor` | Scores recent Claude Code conversations for efficiency, code quality, procedure compliance, and verbosity, then drafts skill edits backed by the conversations that went badly. It writes a Markdown report to a temp directory and never edits your skills on its own. Needs Python 3.9 or later. |
| `/resolve-merge-conflicts` (Auto) | Resolves a stopped merge, rebase, cherry-pick, or stash pop. It reads why each side changed, then shows only the conflict hunks through a script instead of whole files. Needs Python 3.9 or later. |

## Repository layout

```
skills/        one folder per skill
agents/        subagent definitions pstack spawns: poteto-agent and comment-sicko
licenses/      licenses of the copied skill sets
PORTING.md     how pstack is adapted from Cursor to Claude Code
MAINTAINING.md how the copied skills are updated from upstream
```

## Credits and license

The copied skills belong to their authors and keep their licenses:

- pstack, by Lauren Tan, is MIT. See `licenses/pstack.txt`.
- Matt Pocock's skills are MIT. See `licenses/mattpocock-skills.txt`.
- `/clean-mode` adapts ub-mode by Robert C. Martin, which is MIT. See `skills/clean-mode/LICENSE-ub-mode`.
- crapper, dryer, and mutator, by Robert C. Martin, are 0BSD. See the `LICENSE` file in each folder under `skills/clean-mode/tools/`.

Everything else is mine, under the MIT license in [LICENSE](LICENSE).
