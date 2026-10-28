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
backend/            Python 3.15+, uv, FastAPI, uvicorn, psycopg (3), pytest, ruff
  app/
    main.py         FastAPI app, routes
    db.py           connection + queries (plain SQL, no ORM)
    models.py       pydantic request/response models
    migrate.py      applies db/migrations/*.sql in order, idempotently
  tests/
    test_products.py   API tests against a real Postgres (docker) using TestClient
  pyproject.toml    deps, ruff config
frontend/           Vite + React + TypeScript (react-ts template; keep it small), oxlint, Prettier, Vitest
  src/
    App.tsx         list + create form, fetch('/api/products')
    types.ts        `Product { id: number; name: string }`
    App.test.tsx    Vitest + React Testing Library, `fetch` mocked
    setupTests.ts   jest-dom matchers, cleanup after each test
  vite.config.ts    dev server on 3000, proxy /api -> $API_URL or http://localhost:8000, Vitest (jsdom)
  package.json      scripts: dev, build, lint (oxlint), format (prettier --write src), typecheck (tsc -b), test (vitest)
db/
  migrations/
    V001__create_products.sql
docker-compose.yml  one service: postgres:16, db/user/password all "products", port 5432, volume pgdata
.pre-commit-config.yaml  hooks on every commit: whitespace/YAML checks, ruff, pytest, oxlint, prettier, tsc, vitest
```

Repo tooling: `plugins/cr-interview/` (skills), `.claude-plugin/marketplace.json` (marketplace manifest), `.github/pull_request_template.md`, `.worktrees/` (gitignored task worktrees), `.run/` (gitignored server logs and PIDs from `start-application`).

Design choices:
- Plain SQL with psycopg, no ORM. Two queries do not justify SQLAlchemy, and plain SQL is easier to extend.
- Migrations are numbered SQL files applied by a tiny Python runner that tracks applied files in a `schema_migrations` table. Flyway-style, hand-rolled in ~30 lines. Files use Flyway's `V<n>__<name>.sql` naming so Flyway can replace the runner later. Adding a column is: new file, run migrate. Additive migrations (nullable column) are backward compatible, so code can roll back without the schema; drops and renames take two deploys.
- Backend tests hit a real Postgres via docker, not mocks. Frontend tests mock `fetch`.
- Frontend is TypeScript (Vite react-ts template), one component, one `Product` type, no state library, no CSS beyond what Vite ships.
- Vite proxies `/api` to the backend so no CORS config is needed.
- Ruff lints and formats Python (replaces flake8, isort, black). oxlint and Prettier do the same for the frontend, and TypeScript 7 (`tsc`) type-checks it. `pre-commit` runs them plus pytest and Vitest on each commit.

## Commands

```sh
uv tool install pre-commit && pre-commit install         # git hooks, once per clone
pre-commit run --all-files                               # all hooks, all files
docker compose up -d db                                  # postgres
cd backend && uv sync && uv run python -m app.migrate    # schema
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd backend && uv run pytest
cd frontend && npm install && npm run dev                # http://localhost:3000
cd frontend && npm test -- --run
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
3. Commits run the pre-commit hooks. If a commit fails, read the hook output, fix the cause (re-stage files the hooks auto-fixed), and commit again. Never use `--no-verify`.
4. After each step, one line on what changed and why.

## Running and debugging

- `/cr-interview:start-application` starts Postgres, the backend, and the frontend for the current checkout or worktree. It reuses this checkout's servers and picks free ports when another worktree holds 3000 or 8000. Its `stop.sh` stops only the servers it started; Docker and Postgres stay up.
- To debug: run `/cr-interview:start-application`, read the server logs it reports (`.run/backend.log`, `.run/frontend.log`), query data with `/cr-interview:db-query`, and reproduce UI bugs at the URL it reports with Claude in Chrome (`mcp__claude-in-chrome__*` tools).

## Git and task workflow

- Tasks live in the "Project backlog" GitHub issue. Use `/cr-interview:create-todo` to add one, `/cr-interview:implement-task` to build one (commits, pushes, opens a PR), `/cr-interview:merge-pr` to merge it and check off the todo.
- Increment the plugin `version` in `.claude-plugin/marketplace.json` when adding, updating, or deleting any skill; installed copies refresh only when it changes.
- `implement-task` works in a git worktree at `.worktrees/<slug>` on a branch off `origin/main`, so several Claude windows can work in parallel. Never commit directly to `main`; every change lands via a PR targeting `main`.
