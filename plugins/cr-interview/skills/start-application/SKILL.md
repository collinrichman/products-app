---
name: start-application
description: Use when the user asks to "start the app", "run the app", "stop the app", or before verifying or debugging a change in the running app. Starts Postgres, the backend, and the frontend for the current checkout, or stops them.
---

# Start Application

Run the app from the current checkout or worktree, side by side with other worktrees.

## Steps

1. With the working directory inside the checkout, run `<this skill's directory>/scripts/start.sh`. It:
   - starts Docker Desktop if needed, then `docker compose up -d --wait db`
   - migrates, then installs backend and frontend dependencies
   - starts the backend (8000) and frontend (3000) in the background and waits until both respond
   - reuses this checkout's servers; if another checkout holds a port, it uses the next free one
2. Report the App URL, the log paths, and the stop command it prints.
3. To stop, run `<this skill's directory>/scripts/stop.sh` the same way. It stops only the servers `start.sh` started in this checkout.

## Rules

- Never stop Docker, Postgres, or servers from another checkout or session.
- On failure, read the log tail it prints and fix the cause before retrying.
