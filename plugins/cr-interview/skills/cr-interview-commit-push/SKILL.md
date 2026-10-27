---
name: cr-interview-commit-push
description: Use when the user asks to "commit and push", "commit-push", "ship my changes", or "push everything". Reviews all uncommitted changes, commits them in one or more logical commits, and pushes, stopping early if anything is not ready.
disable-model-invocation: true
---

# Commit and Push

Review uncommitted changes, commit them, and push, stopping to report if anything looks unready.

## Steps

1. Run `git status`, `git diff`, and `git diff --staged`. Read every change, including untracked files.
2. Stop and report, committing nothing, if any of these show up:
   - Secrets, `.env` files, credentials, or large/binary artifacts.
   - Debug leftovers (`print`, `console.log`, `TODO` stubs), merge conflict markers, or half-finished edits.
   - Unrelated changes that cannot be grouped sensibly.
   - Any company name or branding in the repo.
   - Files outside this repo folder.
3. Run the relevant checks (`uv run pytest` in `backend/`, `npm run build` in `frontend/`) when those areas changed. Stop on failure, showing the output.
4. Group changes by purpose. Use one commit when they belong together, several when they are distinct. Stage files by name, never `git add -A`.
5. Write each message in the style of `git log --oneline`, imperative, explaining why when not obvious. End with the attribution lines from the session's system-reminder.
6. Before pushing, check the branch with `git branch --show-current` and `git status -sb`. Stop if on a detached HEAD, if the remote is missing, or if the branch is behind or diverged from upstream. Never force push.
7. Push with `git push` (add `-u origin <branch>` if no upstream is set).
8. Report the commits made and the push result in a few lines.
