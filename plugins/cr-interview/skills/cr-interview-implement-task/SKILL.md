---
name: cr-interview-implement-task
description: Use when the user asks to "implement a task", "implement #12", "work on issue 12", "build X and open a PR", or hands over a feature, bugfix, or chore. Implements it end to end in a git worktree off origin/main and ends with a PR to main.
disable-model-invocation: true
---

# Implement Task

Take one task (a GitHub issue number or ad-hoc text) from nothing to an open PR, in an isolated worktree so other Claude windows can work in parallel.

## Steps

1. Resolve the task. For an issue, run `gh issue view <n> --json title,body`; if it is a child of "Project backlog", note that. Ad-hoc text is the task as given. Ask only if the intent is truly ambiguous.
2. Run `git fetch origin`, then `git worktree add -b <type>/<slug> .worktrees/<slug> origin/main` (type: feat, fix, chore, docs; slug from the task, with the issue number when there is one). Do all work inside that worktree. Never touch the main checkout.
3. Read the code the task touches and follow its patterns. Follow the Writing and Code rules in CLAUDE.md for all docs, comments, commits, and PR text, and for the code itself.
4. Implement in full. Add or update tests that fit the task (bugfix: failing test first; feature: API tests against real Postgres; docs or skill changes: validate instead). Keep scope to the task.
5. Run every relevant check and fix failures: `uv run pytest` in `backend/`, `npm run build` in `frontend/`, `claude plugin validate .` for plugin changes. Never skip or weaken a test to go green.
6. Review `git diff` for secrets, debug leftovers, duplicated or needlessly clever code, wordy docs, company branding, and unrelated changes. Commit in logical commits, staging files by name. End messages with the attribution lines from the session's system-reminder.
7. Run `git push -u origin <branch>` (never force), then `gh pr create --base main --body-file <file>`, where the file is `.github/pull_request_template.md` filled in briefly (drop `Closes #` when there is no issue). End the body with the PR attribution line from the system-reminder.
8. Report only the PR URL and a what/why/how overview that reads in 30 seconds, plus anything the user must decide or do.

## Rules

- Never commit or push to `main`. Push only the feature branch, and stop if `git branch --show-current` says `main`.
- Every change reaches `main` through a PR, never a direct push, even for one-line or docs changes.
