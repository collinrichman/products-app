# Products app

React frontend, Python FastAPI backend, Postgres database. List products and create a product.

```
backend/                  FastAPI service (Python, uv)
frontend/                 React + TypeScript (Vite)
db/migrations/            plain SQL, applied in order
docker-compose.yml        local Postgres
plugins/cr-interview/     Claude Code skills for working on this repo
.claude-plugin/           plugin marketplace manifest
.github/                  PR template
CLAUDE.md                 rules for Claude Code
```

## Prerequisites

macOS, starting from a clean machine:

```sh
# Homebrew (also installs git via the Xcode command line tools)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3.15+, uv, Node 20.19+, psql client, Docker Desktop (runs Postgres 16)
brew install python uv node libpq
brew link --force libpq
brew install --cask docker
open -a Docker    # finish the first-run prompts, wait for the engine to start

git clone https://github.com/collinrichman/products-app.git
cd products-app
```

## Database setup

In Claude Code, `/cr-interview:start-application` does this section and the next two in one step: it starts Postgres, migrates, starts both servers in the background, and prints the app URL and log paths. Ask Claude to "stop the app" to stop the servers. The manual steps follow.

```sh
docker compose up -d --wait db
uv run --directory backend python -m app.migrate
```

`db` is Postgres 16 on port 5432, user, password, and database all `products`, data in the `pgdata` volume. `docker compose down -v` deletes the data.

`DATABASE_URL` defaults to `postgresql://products:products@localhost:5432/products`.

## Start backend

In its own terminal, from the repo root:

```sh
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

API: `GET /products`, `POST /products` (body `{"name": "P1", "popularity": 5}`, popularity optional, default 0), `GET /products/search?prefix=p` (case-insensitive name prefix, top 100 by popularity). Docs at http://localhost:8000/docs.

Tests: `cd backend && uv run pytest`

## Start frontend

In a second terminal, from the repo root:

```sh
cd frontend
npm install
npm run dev
```

Serves http://localhost:3000 and proxies `/api` to port 8000 (`API_URL` overrides the target).

Tests: `cd frontend && npm test -- --run`

## Verify

Open http://localhost:3000, create a product named `P1`, and confirm it stays in the list after a refresh. Or:

```sh
curl -s -X POST localhost:8000/products -H 'content-type: application/json' -d '{"name":"P1"}'
curl -s localhost:8000/products
curl -s 'localhost:8000/products/search?prefix=p'
```

## Notes

- Backend is Python (FastAPI) instead of Java Spring Boot. I use Python daily at my current job.
- For Java reviewers: FastAPI routes ≈ Spring Boot controllers, pydantic models ≈ DTOs, and `app.migrate` ≈ Flyway (files use Flyway's `V<n>__<name>.sql` naming).
- Built with Claude Code.
- Lint: ruff (Python), oxlint, Prettier, and tsc (frontend). Hooks also run pytest and Vitest. Run every hook on every file with `pre-commit run --all-files`. The pytest hook needs the database up.

## Contributing

This repo is also a Claude Code plugin marketplace (`cr-interview`). Install it with:

```sh
/plugin marketplace add collinrichman/products-app
/plugin install cr-interview@cr-interview
```

Or load it from a checkout: `claude --plugin-dir ./plugins/cr-interview`.

Git hooks run lint, format, and tests on every commit. Install them once per clone:

```sh
uv tool install pre-commit
pre-commit install
```

Every change lands through a PR to `main`, one Claude window per task:

1. `/cr-interview:create-todo`: add a task to the "Project backlog" issue.
2. `/cr-interview:implement-task`: build it in a worktree (`.worktrees/<slug>`) and open a PR.
3. `/cr-interview:merge-pr`: squash-merge, clean up, check off the todo, and pull `main`.

Running:

- `/cr-interview:start-application`: start Postgres, the backend, and the frontend for the current checkout or worktree, on free ports if another worktree holds 3000 or 8000. Logs go to `.run/`.

Database:

- `/cr-interview:db-migration`: write the next `db/migrations` file, apply it after approval, and run the tests. `implement-task` runs it when a task changes the schema.
- `/cr-interview:db-query`: answer a question with read-only SQL against the local database.

New skills: `/cr-interview:skill-creator`. Bump the plugin version in `.claude-plugin/marketplace.json` on any skill change.
