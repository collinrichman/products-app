---
name: cr-interview-create-todo
description: Use when the user asks to "add a todo", "create a todo", "add to the backlog", or "prioritize a todo". Adds a todo to the Project backlog issue, with a child issue when the todo is complex.
disable-model-invocation: true
---

# Create Todo

Add a todo to the parent issue titled "Project backlog" under **Prioritized** or **Backlog**.

## Steps

1. Find the parent: `gh issue list --state all --search "Project backlog in:title" --json number,title`.
2. Ask which section if unclear: **Prioritized** (do next) or **Backlog** (nice to have).
3. Keep todo and issue text short, per the Writing rules in CLAUDE.md.
4. Decide complexity. Simple means one line of work. Complex means multiple steps or needing a "Done when" criterion.
5. If complex, open a child issue with `gh issue create`: a one-sentence summary, a checklist, and a **Done when:** line. Note the new number.
6. Read the parent body with `gh issue view <n> --json body -q .body`. Append `- [ ] <todo>` (plus ` #<child>` if one exists) to the chosen section. Remove the `_None yet._` placeholder if the section had it.
7. Write the body back with `gh issue edit <n> --body-file <file>`, using a file in the scratchpad.
8. Report the todo line and the child issue URL, if any.
