---
name: cr-interview-merge-pr
description: Use when the user asks to "merge the PR", "approve and merge", "merge #7", "complete a todo", or "check off a todo". Merges a PR to main, then checks off the matching todos in the Project backlog and closes their issues.
disable-model-invocation: true
---

# Merge PR

Merge a PR to `main`, clean up its worktree, and mark the finished todos complete.

## Steps

1. Pick the PR: the number given, else the one for the current branch (`gh pr view --json number,headRefName,body`). Ask if unclear.
2. Check `gh pr view <n> --json state,mergeable,statusCheckRollup`. Stop and report if it is not open, has conflicts, or has failing checks. Skip approval; GitHub does not let authors approve their own PRs and none is required.
3. Run from the main checkout. If `.worktrees/<slug>` exists for the branch, delete it with `git worktree remove`. Then run `gh pr merge <n> --squash --delete-branch` to merge and delete the remote branch. Confirm the local branch is gone with `git branch --list <branch>`; if not, delete it with `git branch -D <branch>` (squash merges defeat `-d`).
4. Find the parent: `gh issue list --state all --search "Project backlog in:title" --json number,title`. Read its body with `gh issue view <p> --json body -q .body`.
5. Find finished work: the issues named by `Closes #` in the PR body, plus any todo whose linked `#<child>` is now closed. Change `- [ ]` to `- [x]` on those lines only. Write the body back with `gh issue edit <p> --body-file <file>`, using a file in the scratchpad.
6. For each linked child issue still open, confirm its **Done when:** is met, tick its checklist, and run `gh issue close <child> --comment "Done in #<pr>."`.
7. Run `git fetch origin` and report in a few lines: the merge result, the todos checked off, and the issues closed.
