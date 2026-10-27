---
name: cr-interview-complete-todo
description: Use when the user asks to "complete a todo", "check off a todo", "mark a todo done", or "close out a todo". Checks the todo off in the Project backlog issue and closes its child issue if there is one.
disable-model-invocation: true
---

# Complete Todo

Check off a todo in the parent issue titled "Project backlog" and close its child issue.

## Steps

1. Find the parent: `gh issue list --state all --search "Project backlog in:title" --json number,title`.
2. Read its body with `gh issue view <n> --json body -q .body` and match the todo the user named. Ask if the match is ambiguous.
3. Change `- [ ]` to `- [x]` on that line only. Write the body back with `gh issue edit <n> --body-file <file>`, using a file in the scratchpad.
4. If the line links a child issue `#<child>`, confirm its **Done when:** is met, tick its checklist, and run `gh issue close <child> --comment "Done."`.
5. Report what was checked off and which issue was closed, if any.
