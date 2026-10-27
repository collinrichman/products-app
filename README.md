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

- Python 3.12+ and [uv](https://docs.astral.sh/uv/) (`brew install python uv`)
- Node 20+ and npm (`brew install node`)
- Docker Desktop, or a local Postgres 16 on port 5432

## Database setup

```sh
docker compose up -d db
uv run --project backend python -m app.migrate
```

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

- Backend is Python (FastAPI) instead of Java Spring Boot, the language I use daily.
- Built with Claude Code.

## Contributing

This repo is also a Claude Code plugin marketplace (`cr-interview`). Install it with:

```sh
/plugin marketplace add collinrichman/products-app
/plugin install cr-interview@cr-interview
```

Or load it from a checkout: `claude --plugin-dir ./plugins/cr-interview`.

Every change lands through a PR to `main`, one Claude window per task:

1. `/cr-interview:cr-interview-create-todo`: add a task to the "Project backlog" issue.
2. `/cr-interview:cr-interview-implement-task`: build it in a worktree (`.worktrees/<slug>`) and open a PR.
3. `/cr-interview:cr-interview-merge-pr`: squash-merge, clean up, and check off the todo.

New skills: `/cr-interview:cr-interview-skill-creator`. Bump the plugin version in `.claude-plugin/marketplace.json` on any skill change.
