# Maintaining this repo

Notes for the repo owner. To install the skills, see [README.md](README.md).

## Update the copied skills

Run these from a Claude Code session started in this repo:

- `/update-pstack` pulls pstack from cursor/plugins, re-applies the Claude Code port in [PORTING.md](PORTING.md), and checks it with `check-port.sh`.
- `/update-mattpocock` pulls Matt Pocock's skills and merges my local edits back in.

Each skill shows the diff and the conflicts, then commits. Neither one pushes.

clean-mode's tools have no skill. To update crapper, dryer, and mutator, run `./update-clean-mode.sh`. When ub-mode changed upstream, it prints a compare link. Port what applies into `skills/clean-mode/SKILL.md` by hand.

`skill-doctor` and `resolve-merge-conflicts` were copied by hand from warpdotdev/common-skills at `8792394`, and they have no update script. Their scripts and the skill-doctor scorers are upstream's, with two local edits. `collect_sessions.py` also reads global skills from `--claude-home`, so `CLAUDE_CONFIG_DIR` setups get graded. The procedure-compliance scorer names CLAUDE.md instead of WARP.md. Upstream's Warp-branded HTML report and its bundled diff viewer were dropped, so skill-doctor writes Markdown. Both SKILL.md files are rewritten, so merge upstream changes into them by hand.

After an update adds or drops a skill, or after I add one of my own, update the tables in `README.md`.

## Set up a new machine

I run two Claude Code workspaces, each started with its own `CLAUDE_CONFIG_DIR`, either `~/.claude-personal` or `~/.claude-work`. Both config dirs link the whole `skills` and `agents` folders to one clone, so a new skill shows up in both workspaces without another step.

1. Clone the repo:

   ```bash
   REPO=~/ramonak/skills
   gh repo clone KaterinaLupacheva/skills "$REPO"
   ```

2. Move any existing `skills` or `agents` folder in either config dir to a `.bak` name. Copy any of my own skills from the backups into `$REPO/skills`.

3. Create the links:

   ```bash
   for dir in ~/.claude-personal ~/.claude-work; do
   	ln -s "$REPO/skills" "$dir/skills"
   	ln -s "$REPO/agents" "$dir/agents"
   done
   ```

4. Start each workspace and check that `/poteto-mode` autocompletes and `/agents` lists `poteto-agent` and `comment-sicko`. Then delete the `.bak` folders.

`/setup-pstack` writes `~/.claude/pstack-models.md`. Both workspaces read that one file.
