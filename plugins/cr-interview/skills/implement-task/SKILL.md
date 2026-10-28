---
name: implement-task
description: Use when the user asks to "implement a task", "implement #12", "work on issue 12", "build X and open a PR", or hands over a feature, bugfix, or chore. Implements it end to end in a git worktree off origin/main and ends with a PR to main.
disable-model-invocation: true
---

# Implement Task

Take one task (a GitHub issue number or ad-hoc text) from nothing to an open PR, in an isolated worktree so other Claude windows can work in parallel.

## Steps

1. Resolve the task. For an issue, run `gh issue view <n> --json title,body`; if it is a child of "Project backlog", note that. Ad-hoc text is the task as given. Ask only if the intent is truly ambiguous.
2. Run `git fetch origin`, then `git worktree add -b <type>/<slug> .worktrees/<slug> origin/main` (type: feat, fix, chore, docs; slug from the task, with the issue number when there is one). Do all work inside that worktree. Never touch the main checkout. Install dependencies so the commit hooks can run: `uv sync --directory backend` and `npm ci --prefix frontend`.
3. Read the code the task touches and follow its patterns. Follow the Writing and Code rules in CLAUDE.md for all docs, comments, commits, and PR text, and for the code itself.
4. If the task changes the schema, run `/cr-interview:db-migration` first, including its approval gate, then continue with the code.
5. Implement in full. Write tests first or alongside, run them red, then green. Add or update tests that fit the task (bugfix: failing test first; backend: API tests against real Postgres; frontend: Vitest + React Testing Library tests next to the component; docs or skill changes: validate instead). Keep scope to the task.
6. Run the checks the commit hooks do not: `npm run build` in `frontend/`, `claude plugin validate .` for plugin changes. The hooks run lint, format, typecheck, pytest, and Vitest on commit. Never skip or weaken a test to go green.
7. Verify end to end from the worktree. Run `/cr-interview:start-application`, then use the change as a user would: backend changes, `curl` the affected endpoints at the backend URL it reports; frontend changes, Claude in Chrome (`mcp__claude-in-chrome__*` tools) at the App URL it reports; docs or skill changes, follow or run them as written. Afterwards, pass or fail, run its stop step. Leave Docker and Postgres running. On a failure, fix it and verify again.
8. Review `git diff` for secrets, debug leftovers, duplicated or needlessly clever code, wordy docs, company branding, and unrelated changes. Commit in logical commits, staging files by name. End messages with the attribution lines from the session's system-reminder. Commits run the pre-commit hooks; if one fails, read the output, fix the cause, re-stage (including files the hooks auto-fixed), and commit again. Never use `--no-verify`.
9. Run `git push -u origin <branch>` (never force), then `gh pr create --base main --body-file <file>`, where the file is `.github/pull_request_template.md` filled in briefly (drop `Closes #` when there is no issue). The Testing section lists the tests and each end-to-end check. End the body with the PR attribution line from the system-reminder.
10. Report only the PR URL, a what/why/how overview that reads in 30 seconds, what was verified end to end, and anything the user must decide or do.

## Rules

- Never commit or push to `main`. Push only the feature branch, and stop if `git branch --show-current` says `main`.
- Every change reaches `main` through a PR, never a direct push, even for one-line or docs changes.
