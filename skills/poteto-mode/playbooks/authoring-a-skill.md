### Authoring or modifying a skill

**You own the skill's voice.**

1. Write the `SKILL.md` yourself. Claude Code has no skill-authoring built-in. The format:
   - One directory per skill, holding `SKILL.md`. Project skills live in `.claude/skills/<name>/`, personal skills in `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/<name>/`, bundled skills in a plugin's `skills/` directory.
   - Frontmatter carries `name` (lowercase letters, digits, and hyphens, matching the directory) and `description` as a single YAML scalar. The description is the only thing the model sees when deciding to load the skill, so it names both what the skill does and the phrasings that should trigger it. Add `disable-model-invocation: true` for a skill only a human should start with `/<name>`, and `allowed-tools` to narrow what it may call.
   - Keep the body short and put the bulk in `references/*.md` the skill opens on demand. The body is loaded in full every time the skill fires.
2. Validate the skill: frontmatter has a well-formed `name` and `description`, the name matches the directory, referenced files exist, cross-skill links resolve. Run `/skill-doctor` when it is available.
3. Test cases if structural. Skip if subjective.
4. Run **Opening a PR**.

When in doubt, delete. Keep only prose that changes a decision. Tell it to do the thing and skip the reason. Explain only when the rule is confusing without one. Match tone to scope. Point at structural sources (types, READMEs, config) per the **encode-lessons-in-structure** principle skill. Delegate to other skills by path. Don't restate. A workflow you keep hitting but isn't captured → propose a new skill.

**Reply:** summary of the skill, key design decisions, validation notes.
