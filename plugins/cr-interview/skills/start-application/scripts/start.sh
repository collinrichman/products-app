#!/usr/bin/env bash
# Start Postgres, the backend, and the frontend for the current checkout.
# Reuses this checkout's servers; never touches servers from other checkouts.
#
# Run it from anywhere inside a checkout or worktree. When it finishes, it
# prints the app URL, where the logs are, and how to stop the servers.

# Stop at the first failing command (-e), treat unset variables as errors (-u),
# and fail a pipeline if any part of it fails (pipefail).
set -euo pipefail
# Give each background server its own process group, so stop.sh can end the
# server and every process it spawned in one go.
set -m

# The top folder of the checkout this is run from, e.g. the main clone or
# .worktrees/<slug>. Everything below works relative to it.
root=$(git rev-parse --show-toplevel)
# Per-checkout folder (gitignored) for server logs, process IDs, and ports.
run="$root/.run"
mkdir -p "$run"

# Print the folder the process listening on a port was started from, or print
# nothing if the port is free. That folder tells us which checkout owns it.
port_owner() {
  local pid
  # lsof lists open files and ports; -t prints only the process ID.
  pid=$(lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null | head -1) || true
  # -d cwd asks for the process's working directory; sed strips lsof's "n" prefix.
  [ -n "$pid" ] && lsof -a -p "$pid" -d cwd -Fn | sed -n 's/^n//p'
}

# Succeed if a folder belongs to this checkout. Worktrees live inside the main
# clone under .worktrees/, so those count as other checkouts, not this one.
in_checkout() {
  case "$1" in
    "$root/.worktrees/"*) return 1 ;;
    "$root"/*) return 0 ;;
    *) return 1 ;;
  esac
}

# Poll a URL once a second for up to 60 seconds until it answers.
# If it never does, show the end of the server's log and exit with an error.
wait_for() {
  for _ in $(seq 60); do
    curl -sf "$1" >/dev/null && return 0
    sleep 1
  done
  echo "Timed out waiting for $1. Log: $2" >&2
  tail -20 "$2" >&2
  exit 1
}

# Start one server, or reuse it if this checkout already has it running.
# Usage: start_server <name> <default port> <health path> <command...>
# Afterwards $port holds the port the server is on.
start_server() {
  local name=$1 health=$3 owner
  port=$2
  # Drop the first three arguments; what is left ("$@") is the command to run.
  shift 3

  # Already started by this script earlier and still alive? Reuse it.
  # (kill -0 sends no signal; it only checks that the process exists.)
  if [ -f "$run/$name.pid" ] && kill -0 "$(cat "$run/$name.pid")" 2>/dev/null; then
    port=$(cat "$run/$name.port")
    echo "$name: reusing server started by this skill on $port"
    return
  fi

  # Walk up from the default port until one is free. A server on that port
  # from this checkout (e.g. started by hand) is reused. One from another
  # checkout is left alone and skipped.
  while owner=$(port_owner "$port"); [ -n "$owner" ]; do
    if in_checkout "$owner"; then
      echo "$name: reusing server from this checkout on $port"
      return
    fi
    echo "$name: port $port is used by $owner, trying $((port + 1))"
    port=$((port + 1))
  done

  # Run the server in the background (&). nohup keeps it running after this
  # script exits, and all its output goes to the log file.
  PORT=$port nohup "$@" >"$run/$name.log" 2>&1 &
  # $! is the background process's ID. Save it and the port for stop.sh and reruns.
  echo $! >"$run/$name.pid"
  echo "$port" >"$run/$name.port"
  wait_for "http://localhost:$port$health" "$run/$name.log"
  echo "$name: started on $port"
}

# Make sure Docker is running. If not, open Docker Desktop and wait up to two
# minutes for it to be ready.
if ! docker info >/dev/null 2>&1; then
  echo "Starting Docker Desktop"
  open -a Docker
  for _ in $(seq 120); do docker info >/dev/null 2>&1 && break; sleep 1; done
fi
# Start Postgres (shared by every checkout) and wait until it is healthy.
docker compose -f "$root/docker-compose.yml" up -d --wait db
# Apply database migrations. uv run also installs backend dependencies first.
uv run --directory "$root/backend" python -m app.migrate
# Install frontend dependencies (quick when already installed).
npm install --prefix "$root/frontend" --silent

# Backend: FastAPI on 8000 (or the next free port). Ready when /products answers.
# `exec` replaces the wrapper shell with uv, so the saved process ID is the server's.
cd "$root/backend"
start_server backend 8000 /products sh -c 'exec uv run uvicorn app.main:app --reload --port $PORT'
backend_port=$port

# Frontend: Vite on 3000 (or the next free port), forwarding /api to the backend
# above. Ready when /api/products answers, which proves the forwarding works.
cd "$root/frontend"
export API_URL="http://localhost:$backend_port"  # vite.config.ts proxies /api here
start_server frontend 3000 /api/products sh -c 'exec npm run dev -- --port $PORT --strictPort'

echo
echo "App:      http://localhost:$port"
echo "Backend:  http://localhost:$backend_port"
echo "Logs:     $run/backend.log, $run/frontend.log"
echo "Stop:     $(dirname "$0")/stop.sh"
