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

# Python 3.15+, uv, Node 20.19+, psql client, Docker Desktop
brew install python uv node libpq
brew link --force libpq
brew install --cask docker
open -a Docker    # finish the first-run prompts, wait for the engine to start

git clone https://github.com/collinrichman/products-app.git
cd products-app

# git hooks: lint, format, and tests run on every commit
uv tool install pre-commit
pre-commit install
```

Docker Desktop can be replaced by a local Postgres 16 on port 5432.

## Database setup

```sh
docker compose up -d --wait db
psql postgresql://products:products@localhost:5432/products -c '\l'
uv run --directory backend python -m app.migrate
```

`db` is Postgres 16 on port 5432, user, password, and database all `products`, data in the `pgdata` volume. `docker compose down -v` deletes the data.

Without Docker:

```sh
createdb products
psql products -f db/migrations/V001__create_products.sql
```

`DATABASE_URL` defaults to `postgresql://products:products@localhost:5432/products`.

## Start backend

```sh
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API: `GET /products`, `POST /products` (body `{"name": "P1"}`). Docs at http://localhost:8000/docs.

Tests: `cd backend && uv run pytest`

## Start frontend

```sh
cd frontend
npm install
npm run dev
```

Serves http://localhost:3000 and proxies `/api` to port 8000.

## Verify

Open http://localhost:3000, create a product named `P1`, and confirm it stays in the list after a refresh. Or:

```sh
curl -s -X POST localhost:8000/products -H 'content-type: application/json' -d '{"name":"P1"}'
curl -s localhost:8000/products
```

## Notes

- Backend is Python (FastAPI) instead of Java Spring Boot. I use python daily at my current job.
- Built with Claude Code.
- Lint: ruff (Python), oxlint, Prettier, and tsc (frontend). Run every hook on every file with `pre-commit run --all-files`. The pytest hook needs the database up.

## Contributing

This repo is also a Claude Code plugin marketplace (`cr-interview`). Install it with:

```sh
/plugin marketplace add collinrichman/products-app
/plugin install cr-interview@cr-interview
```

Or load it from a checkout: `claude --plugin-dir ./plugins/cr-interview`.

Every change lands through a PR to `main`, one Claude window per task:

1. `/cr-interview:create-todo`: add a task to the "Project backlog" issue.
2. `/cr-interview:implement-task`: build it in a worktree (`.worktrees/<slug>`) and open a PR.
3. `/cr-interview:merge-pr`: squash-merge, clean up, check off the todo, and pull `main`.

Database:

- `/cr-interview:db-migration`: write the next `db/migrations` file, apply it after approval, and run the tests. `implement-task` runs it when a task changes the schema.
- `/cr-interview:db-query`: answer a question with read-only SQL against the local database.

New skills: `/cr-interview:skill-creator`. Bump the plugin version in `.claude-plugin/marketplace.json` on any skill change.
