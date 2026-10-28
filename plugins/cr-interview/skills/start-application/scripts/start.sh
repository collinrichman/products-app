#!/usr/bin/env bash
# Start Postgres, the backend, and the frontend for the current checkout.
# Reuses this checkout's servers; never touches servers from other checkouts.
set -euo pipefail
set -m  # each background server gets its own process group, so stop.sh can end it whole

root=$(git rev-parse --show-toplevel)
run="$root/.run"
mkdir -p "$run"

# Prints the cwd of the process listening on a port, or nothing if the port is free.
port_owner() {
  local pid
  pid=$(lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null | head -1) || true
  [ -n "$pid" ] && lsof -a -p "$pid" -d cwd -Fn | sed -n 's/^n//p'
}

# True if a path is in this checkout (worktrees under .worktrees/ are other checkouts).
in_checkout() {
  case "$1" in
    "$root/.worktrees/"*) return 1 ;;
    "$root"/*) return 0 ;;
    *) return 1 ;;
  esac
}

wait_for() {
  for _ in $(seq 60); do
    curl -sf "$1" >/dev/null && return 0
    sleep 1
  done
  echo "Timed out waiting for $1. Log: $2" >&2
  tail -20 "$2" >&2
  exit 1
}

# Usage: start_server <name> <default port> <health path> <command...>
# Sets $port to the port the server is on.
start_server() {
  local name=$1 health=$3 owner
  port=$2
  shift 3
  if [ -f "$run/$name.pid" ] && kill -0 "$(cat "$run/$name.pid")" 2>/dev/null; then
    port=$(cat "$run/$name.port")
    echo "$name: reusing server started by this skill on $port"
    return
  fi
  while owner=$(port_owner "$port"); [ -n "$owner" ]; do
    if in_checkout "$owner"; then
      echo "$name: reusing server from this checkout on $port"
      return
    fi
    echo "$name: port $port is used by $owner, trying $((port + 1))"
    port=$((port + 1))
  done
  PORT=$port nohup "$@" >"$run/$name.log" 2>&1 &
  echo $! >"$run/$name.pid"
  echo "$port" >"$run/$name.port"
  wait_for "http://localhost:$port$health" "$run/$name.log"
  echo "$name: started on $port"
}

if ! docker info >/dev/null 2>&1; then
  echo "Starting Docker Desktop"
  open -a Docker
  for _ in $(seq 120); do docker info >/dev/null 2>&1 && break; sleep 1; done
fi
docker compose -f "$root/docker-compose.yml" up -d --wait db
uv run --directory "$root/backend" python -m app.migrate
npm install --prefix "$root/frontend" --silent

cd "$root/backend"
start_server backend 8000 /products sh -c 'exec uv run uvicorn app.main:app --reload --port $PORT'
backend_port=$port

cd "$root/frontend"
export API_URL="http://localhost:$backend_port"  # vite.config.ts proxies /api here
start_server frontend 3000 /api/products sh -c 'exec npm run dev -- --port $PORT --strictPort'

echo
echo "App:      http://localhost:$port"
echo "Backend:  http://localhost:$backend_port"
echo "Logs:     $run/backend.log, $run/frontend.log"
echo "Stop:     $(dirname "$0")/stop.sh"
