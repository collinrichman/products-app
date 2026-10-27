# Products app

A minimal end-to-end Products app: React frontend, Python FastAPI backend, Postgres database. List products and create a product. Nothing else.

Layout:

```
products-app/
  backend/        FastAPI service (Python, uv)
    app/          application code
    tests/        pytest
  frontend/       React + TypeScript app (Vite)
  db/
    migrations/   plain SQL, applied in order
  docker-compose.yml   local Postgres
```

## Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/) (`brew install python uv`)
- Node 20+ and npm (`brew install node`)
- Docker Desktop (for Postgres), or a local Postgres 16 on port 5432

## Database setup

Start Postgres and create the `products` table:

```sh
docker compose up -d db
uv run --project backend python -m app.migrate   # applies db/migrations/*.sql in order
```

Or, without Docker, against a local Postgres:

```sh
createdb products
psql products -f db/migrations/V001__create_products.sql
```

Connection string defaults to `postgresql://products:products@localhost:5432/products` and can be overridden with `DATABASE_URL`.

## Start backend

```sh
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API: `GET /products`, `POST /products` (body `{"name": "P1"}`). Interactive docs at http://localhost:8000/docs.

Tests:

```sh
cd backend
uv run pytest
```

## Start frontend

```sh
cd frontend
npm install
npm run dev
```

Opens on http://localhost:3000 and proxies `/api` to the backend on port 8000.

## Verify

Open http://localhost:3000, create a product named `P1`, and confirm it appears in the list. Refresh the page; it should still be there.

Or from the terminal:

```sh
curl -s -X POST localhost:8000/products -H 'content-type: application/json' -d '{"name":"P1"}'
curl -s localhost:8000/products
```

## Notes

- **Stack deviation:** backend is Python (FastAPI) instead of Java Spring Boot. Python is the language I use daily; for a live pairing session I'd rather be productive in it than re-learn framework conventions on the clock. The API shape, migration approach, and test layers are the same ideas, just in Python.
- Built with Claude Code assistance. All code reviewed and understood; I'll be extending it live.
- Scope is intentionally minimal per the brief: create and list only, no update/delete, no styling, no production hardening.

## Contributing

Work lands through PRs to `main`; direct pushes are blocked. This repo is also a Claude Code plugin marketplace (`cr-interview`) holding the skills used to work on it. Skills live in `plugins/cr-interview/skills/` and are named `cr-interview-*`.

To load them for a session, run from the repo root:

```sh
claude --plugin-dir ./plugins/cr-interview
```

Alternatively, install it as a marketplace with `/plugin marketplace add collinrichman/products-app`.

Workflow, one Claude window per task:

1. `cr-interview-create-todo`: add a task to the "Project backlog" issue (complex ones get a child issue).
2. `cr-interview-implement-task`: give it an issue number or a description. It works in a git worktree (`.worktrees/<slug>`) on a branch off `origin/main`, tests, commits, pushes, and opens a PR to `main`.
3. `cr-interview-merge-pr`: merges the PR, removes the worktree, checks off the finished todos in the backlog, and closes their issues.

To add a skill, ask Claude Code to use `cr-interview-skill-creator`.
