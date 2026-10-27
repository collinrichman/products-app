# Products app (take-home + live pairing)

## Context

This repo is the scaffold for a 45-minute pair-programming interview on **Wed 2026-10-28, 2:00 PM CT** with two engineers (an SE IV and an SE III). They will start from this working app and extend it live, with Collin driving and Claude Code on screen. AI use is explicitly allowed in both the take-home and the session.

The take-home brief, verbatim where it matters:

- Minimal end-to-end **Products** app: Frontend, Backend, Database. Runs locally.
- **Frontend:** simple UI that lists products and lets the user create one.
- **Backend:** API to list products and create a product.
- **Database:** Postgres table `products` with `id` (auto-generated PK) and `name` (string, required). No other columns.
- **2 hours. Minimal. Runnable.** They build on top of it during the interview.
- **Do not:** implement update or delete; spend time on styling or CSS; harden for production; add any company branding anywhere.
- Preferred stack was React + Spring Boot + Postgres. We are using **React + Python FastAPI + Postgres**, and the README Notes section says so.
- README must have these six headings in this order: Prerequisites, Database setup, Start backend, Start frontend, Verify, Notes. Already written; keep the commands in it true.

What the panel evaluates in the live session (their words): problem understanding and clarification; decomposition, data structures and algorithmic reasoning; correctness and edge cases; readability and maintainability; testing mindset and testing layers; production and systems thinking (stack-agnostic: logging, metrics, error handling, testability, CI/CD, deployment and rollback); pairing and collaboration behaviors. Algorithmic probes will be short and tied to the app.

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

Design choices, so they can be defended live:
- Plain SQL with psycopg, no ORM. Two queries do not justify SQLAlchemy, and plain SQL is easier to extend in front of people.
- Migrations are numbered SQL files applied by a tiny Python runner that tracks applied files in a `schema_migrations` table. This is the Flyway model, hand-rolled because it is ~30 lines and two files do not justify a JVM or Docker step in the README. Files use Flyway's `V<n>__<name>.sql` naming so swapping in real Flyway later is a rename of nothing. Adding a column live is: new file, run migrate, done. Talking point: additive migrations (nullable column) are backward compatible, so code can roll back without the schema; drops and renames take two deploys.
- Tests hit a real Postgres via docker, not mocks. Testing the SQL is the point.
- Frontend is TypeScript (Vite react-ts template), one component, one `Product` type, no state library, no CSS beyond what Vite ships. The brief says no styling. TypeScript costs nothing at this size and matches what the resume says.
- Vite proxies `/api` to the backend so there is no CORS config to explain.

## Commands

```sh
docker compose up -d db                                  # postgres
cd backend && uv sync && uv run python -m app.migrate    # schema
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd backend && uv run pytest
cd frontend && npm install && npm run dev                # http://localhost:3000
```

## Implementation plan (for the build session; check off as you go)

1. `docker-compose.yml` with postgres:16. Verify `docker compose up -d db` and `psql` connects.
2. `db/migrations/V001__create_products.sql`: `id BIGSERIAL PRIMARY KEY`, `name TEXT NOT NULL`. Add a `CHECK (length(trim(name)) > 0)`.
3. `backend/pyproject.toml` via `uv init --app`, then `uv add fastapi "uvicorn[standard]" "psycopg[binary]" pydantic` and `uv add --dev pytest httpx`.
4. `app/migrate.py`: create `schema_migrations(filename text primary key, applied_at timestamptz)` if missing; apply unapplied files in sorted order inside a transaction each.
5. `app/db.py`: `get_conn()` reading `DATABASE_URL` with the default from the README; `list_products()`, `create_product(name)`.
6. `app/models.py`: `ProductCreate(name: str)` with `min_length=1` after strip; `Product(id: int, name: str)`.
7. `app/main.py`: `GET /products` -> list; `POST /products` -> 201 with the created row; 422 on invalid body (FastAPI default); one `logging` line per request handler.
8. `tests/test_products.py`: create then list; empty name -> 422; list is ordered by id. Run green.
9. `frontend/`: `npm create vite@latest . -- --template react-ts`, strip the boilerplate, `src/types.ts` with the `Product` type, `App.tsx` with a list and a one-field form, `vite.config.ts` with port 3000 and the `/api` proxy. Backend routes stay at `/products`; the proxy rewrites `/api/products` -> `/products`.
10. Walk the README top to bottom on a clean shell and fix anything that is not literally true.
11. `git init`, `.gitignore` is already here, commit. Private GitHub repo named `products-app`. Invite the interviewers.

Time-box: 2 hours. If something is not working at 90 minutes, cut scope (e.g. skip the migration runner and use `psql -f`), update the README to match, and ship.

## How to work in the live session

Collin drives. VS Code is a viewer. Claude Code is the typist and a thinking partner, not the decision maker.

1. When the panel describes an extension, restate it in one sentence and suggest one or two clarifying questions for Collin to ask them.
2. State the approach and, where relevant, the cost (query shape, index, complexity) in one or two sentences. Wait for Collin's go-ahead.
3. Tests first or alongside. Run them red, implement, run green. Small commits at each green step.
4. After each step, one line on what changed and why, so Collin can say it out loud in his own words.
5. Readable over clever. Keep the existing patterns: plain SQL in `db.py`, pydantic at the edge, routes thin.
6. Do not add dependencies without Collin saying yes to the panel first.
7. If asked about production: logging (structured, request id), metrics (request count and latency per route), error handling (4xx vs 5xx, no stack traces to clients), testing layers (unit on pure functions, API tests against real Postgres, one e2e), CI (lint, test, build on PR), deploy (container image, rolling deploy), rollback (previous image; migrations must be backward compatible for one version).

Likely extensions to be ready for: add a column (price, sku) with a migration; `GET /products/{id}` with 404; validation and 400/422 behavior; search or filter by name prefix (and when a `LIKE` scan stops being fine); pagination; de-duplication; a unique constraint and the race it closes.

## Do not

- Do not implement update or delete unless the panel asks.
- Do not add CSS, auth, Docker for the app itself, or anything the brief calls hardening.
- Do not put any company name or branding anywhere in the code or repo.
- Do not touch anything outside this folder.

## Working in this repo (outside the live session)

- Tasks live in the "Project backlog" GitHub issue. Use `cr-interview-create-todo` to add one, `cr-interview-implement-task` to build one, `cr-interview-complete-todo` to check it off after merge.
- `implement-task` works in a git worktree at `.worktrees/<slug>` on a branch off `origin/main`, so several Claude windows can work in parallel. Never commit directly to `main`; every change lands via a PR targeting `main`.
- Commit and push are part of `implement-task`; there is no separate commit-push skill.
