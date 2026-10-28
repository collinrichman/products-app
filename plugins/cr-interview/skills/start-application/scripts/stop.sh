#!/usr/bin/env bash
# Stop the servers start.sh started in the current checkout. Leaves Docker and Postgres running.
set -euo pipefail

run="$(git rev-parse --show-toplevel)/.run"

for name in backend frontend; do
  pid_file="$run/$name.pid"
  if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    kill -- -"$(cat "$pid_file")"
    echo "$name: stopped"
  else
    echo "$name: not started by this skill"
  fi
  rm -f "$pid_file" "$run/$name.port"
done
