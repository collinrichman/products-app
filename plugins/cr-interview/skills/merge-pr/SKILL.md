---
name: merge-pr
description: Use when the user asks to "merge the PR", "approve and merge", "merge #7", "complete a todo", or "check off a todo". Merges a PR to main, then checks off the matching todos in the Project backlog and closes their issues.
disable-model-invocation: true
---

# Merge PR

Merge a PR to `main`, clean up its worktree, and mark the finished todos complete.

## Steps

1. Pick the PR: the number given, else the one for the current branch (`gh pr view --json number,headRefName,body`). Ask if unclear.
2. Check `gh pr view <n> --json state,mergeable,statusCheckRollup`. Stop and report if it is not open, has conflicts, or has failing checks.
3. Run from the main checkout. If `.worktrees/<slug>` exists for the branch, delete it with `git worktree remove`. Then run `gh pr merge <n> --squash` (squash only; GitHub deletes the remote branch). Delete the local branch with `git branch -D <branch>` (squash merges defeat `-d`) and run `git fetch --prune origin`.
4. Read the "Project backlog" issue (`gh issue list --search "Project backlog in:title"`, then `gh issue view <n> --json body -q .body`). Change `- [ ]` to `- [x]` for each todo this PR completed and write the body back with `gh issue edit <n> --body-file <file>`.
5. Close each completed todo's child issue, if it has one: `gh issue close <child> --comment "Done in #<pr>."`.
6. In the main checkout, run `git pull --ff-only` if it is on `main`. Otherwise run `git fetch origin` and say `main` was not pulled.
7. Report in a few lines: the merge result, the todos checked off, and the issues closed.

## Rules

- Merge only with `gh pr merge --squash`. Never use merge commits or rebase, and never push to `main` directly.
- Never force push or delete `main`.
