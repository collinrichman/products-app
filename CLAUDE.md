# Products app

React frontend, Python FastAPI backend, Postgres database. Runs locally.

## Scope

- Frontend: simple UI that lists products and lets the user create one.
- Backend: API to list products and create a product.
- Database: Postgres table `products` with `id` (auto-generated PK) and `name` (string, required). No other columns until a task adds one.
- README has these six headings in this order: Prerequisites, Database setup, Start backend, Start frontend, Verify, Notes. Keep its commands true.

## Stack and layout

App:

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

Repo tooling: `plugins/cr-interview/` (skills), `.claude-plugin/marketplace.json` (marketplace manifest), `.github/pull_request_template.md`, `.worktrees/` (gitignored task worktrees).

Design choices:
- Plain SQL with psycopg, no ORM. Two queries do not justify SQLAlchemy, and plain SQL is easier to extend.
- Migrations are numbered SQL files applied by a tiny Python runner that tracks applied files in a `schema_migrations` table. Flyway-style, hand-rolled in ~30 lines. Files use Flyway's `V<n>__<name>.sql` naming so Flyway can replace the runner later. Adding a column is: new file, run migrate. Additive migrations (nullable column) are backward compatible, so code can roll back without the schema; drops and renames take two deploys.
- Tests hit a real Postgres via docker, not mocks.
- Frontend is TypeScript (Vite react-ts template), one component, one `Product` type, no state library, no CSS beyond what Vite ships.
- Vite proxies `/api` to the backend so no CORS config is needed.

## Commands

```sh
docker compose up -d db                                  # postgres
cd backend && uv sync && uv run python -m app.migrate    # schema
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd backend && uv run pytest
cd frontend && npm install && npm run dev                # http://localhost:3000
```

## Writing

Applies to markdown, code comments, issues, PR descriptions, and commit messages.

- Short. Nothing is a long read.
- State what. Add how or why only when not obvious.
- No filler or extrapolation ("Nothing else.", "we chose not to...").
- Describe what exists. Do not state what is missing, not done, or planned.

## Code

- Clean, readable, DRY. A human should follow it at a glance.
- Simple classes and functions that do one job. No cleverness, no speculative abstraction.
- Keep the existing patterns: plain SQL in `db.py`, pydantic at the edge, routes thin.

## Working rules

1. State the approach and, where relevant, the cost (query shape, index, complexity) in one or two sentences. Wait for a go-ahead on anything non-trivial.
2. Tests first or alongside. Run them red, implement, run green. Small commits at each green step, on the task's feature branch.
3. After each step, one line on what changed and why.

## Git and task workflow

- Tasks live in the "Project backlog" GitHub issue. Use `cr-interview-create-todo` to add one, `cr-interview-implement-task` to build one (commits, pushes, opens a PR), `cr-interview-merge-pr` to merge it and check off the todo.
- Increment the plugin `version` in `.claude-plugin/marketplace.json` when adding, updating, or deleting any skill; installed copies refresh only when it changes.
- `implement-task` works in a git worktree at `.worktrees/<slug>` on a branch off `origin/main`, so several Claude windows can work in parallel. Never commit directly to `main`; every change lands via a PR targeting `main`.
