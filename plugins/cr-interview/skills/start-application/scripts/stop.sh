#!/usr/bin/env bash
# Stop the servers start.sh started in the current checkout. Leaves Docker and Postgres running.
#
# Servers started by hand, or by another checkout or session, are left alone:
# only process IDs that start.sh saved in this checkout's .run/ folder are stopped.

# Stop at the first failing command, treat unset variables as errors, and fail
# a pipeline if any part of it fails.
set -euo pipefail

# This checkout's .run/ folder, where start.sh saved process IDs and ports.
run="$(git rev-parse --show-toplevel)/.run"

for name in backend frontend; do
  pid_file="$run/$name.pid"
  # Only act if start.sh saved a process ID and that process is still alive.
  # (kill -0 sends no signal; it only checks that the process exists.)
  if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    # The minus sign targets the whole process group, so the server and every
    # process it spawned (e.g. uvicorn's reload worker) stop together.
    kill -- -"$(cat "$pid_file")"
    echo "$name: stopped"
  else
    echo "$name: not started by this skill"
  fi
  # Forget the saved process ID and port so the next start begins fresh.
  rm -f "$pid_file" "$run/$name.port"
done
