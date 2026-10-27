---
name: cr-interview-skill-creator
description: Use when the user asks to "create a skill", "add a skill", "make a skill for X", or "save this as a skill". Scaffolds a short, focused skill in this repo's cr-interview plugin.
---

# Skill Creator

Create one simple skill in `plugins/cr-interview/skills/`.

## Steps

1. Ask what the skill does and what the user would say to trigger it. Skip questions already answered.
2. Name it `cr-interview-<verb-noun>` in kebab-case (e.g. `cr-interview-create-todo`).
3. Create `plugins/cr-interview/skills/<name>/SKILL.md` using the template below.
4. Run `claude plugin validate .` from the repo root and fix any errors.
5. Bump the plugin `version` in `.claude-plugin/marketplace.json` (minor for a new skill). Installed copies refresh only when it changes.
6. Commit the new skill.

## Template

```markdown
---
name: <name>
description: Use when the user asks to "<phrase 1>", "<phrase 2>", or <situation>. <One sentence on what it does.>
---

# <Title>

<One sentence overview.>

## Steps

1. <Imperative step.>
2. <Imperative step.>
```

## Rules

- Follow the Writing rules in CLAUDE.md. Keep SKILL.md under 40 lines. Cut anything Claude already knows.
- Write the description for triggering: 2-3 quoted user phrases, imperative "Use when...".
- Write the body as imperative steps, with no second person.
- Add `disable-model-invocation: true` to the frontmatter if the skill has side effects (commits, closing issues).
- Add `references/` or `scripts/` only when a skill truly needs them.
- Do not add a version to `plugin.json`. Versions live in `.claude-plugin/marketplace.json`.
- Bump that version on every skill add, update, or delete.
