# Products app

Minimal end-to-end Products app: React frontend, Python FastAPI backend, Postgres database. Runs locally.

## Scope

- Frontend: simple UI that lists products and lets the user create one.
- Backend: API to list products and create a product.
- Database: Postgres table `products` with `id` (auto-generated PK) and `name` (string, required). No other columns until a task adds one.
- README has these six headings in this order: Prerequisites, Database setup, Start backend, Start frontend, Verify, Notes. Keep its commands true.

## Stack and layout

```
backend/            Python 3.12+, uv, FastAPI, uvicorn, psycopg (3), pytest
  app/
    main.py         FastAPI app, routes
    db.py           connection + queries (plain SQL, no ORM)
    models.py       pydantic request/response models
    migrate.py      applies db/migrations/*.sql in order, idempotently
  tests/
    test_products.py   API tests against a real Postgres (docker) using TestClient
  pyproject.toml
frontend/           Vite + React + TypeScript (react-ts template; keep it small)
  src/
    App.tsx         list + create form, fetch('/api/products')
    types.ts        `Product { id: number; name: string }`
  vite.config.ts    dev server on 3000, proxy /api -> http://localhost:8000
db/
  migrations/
    V001__create_products.sql
docker-compose.yml  one service: postgres:16, db/user/password all "products", port 5432
```

Design choices:
- Plain SQL with psycopg, no ORM. Two queries do not justify SQLAlchemy, and plain SQL is easier to extend.
- Migrations are numbered SQL files applied by a tiny Python runner that tracks applied files in a `schema_migrations` table. This is the Flyway model, hand-rolled because it is ~30 lines and two files do not justify a JVM or Docker step in the README. Files use Flyway's `V<n>__<name>.sql` naming so swapping in real Flyway later is a rename of nothing. Adding a column is: new file, run migrate. Additive migrations (nullable column) are backward compatible, so code can roll back without the schema; drops and renames take two deploys.
- Tests hit a real Postgres via docker, not mocks. Testing the SQL is the point.
- Frontend is TypeScript (Vite react-ts template), one component, one `Product` type, no state library, no CSS beyond what Vite ships. TypeScript costs nothing at this size.
- Vite proxies `/api` to the backend so no CORS config is needed.

## Commands

```sh
docker compose up -d db                                  # postgres
cd backend && uv sync && uv run python -m app.migrate    # schema
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd backend && uv run pytest
cd frontend && npm install && npm run dev                # http://localhost:3000
```

## Working rules

1. State the approach and, where relevant, the cost (query shape, index, complexity) in one or two sentences. Wait for a go-ahead on anything non-trivial.
2. Tests first or alongside. Run them red, implement, run green. Small commits at each green step, on the task's feature branch.
3. After each step, one line on what changed and why.
4. Readable over clever. Keep the existing patterns: plain SQL in `db.py`, pydantic at the edge, routes thin.
5. Do not add dependencies without asking.
6. Production concerns: logging (structured, request id), metrics (request count and latency per route), error handling (4xx vs 5xx, no stack traces to clients), testing layers (unit on pure functions, API tests against real Postgres, one e2e), CI (lint, test, build on PR), deploy (container image, rolling deploy), rollback (previous image; migrations must be backward compatible for one version).

## Do not

- Do not implement update or delete unless a task asks.
- Do not add CSS, auth, Docker for the app itself, or production hardening.
- Do not put any company name or branding anywhere in the code or repo.
- Do not touch anything outside this folder.

## Git and task workflow

- Tasks live in the "Project backlog" GitHub issue. Use `cr-interview-create-todo` to add one, `cr-interview-implement-task` to build one (commits, pushes, opens a PR), `cr-interview-merge-pr` to merge it and check off the todo.
- `implement-task` works in a git worktree at `.worktrees/<slug>` on a branch off `origin/main`, so several Claude windows can work in parallel. Never commit directly to `main`; every change lands via a PR targeting `main`.
