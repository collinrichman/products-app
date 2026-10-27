---
name: cr-interview-db-migration
description: Use when the user asks to "add a column", "add a table", "write a migration", or a task changes the database schema. Writes the next db/migrations SQL file, gets approval, applies it, and runs the tests.
disable-model-invocation: true
---

# DB Migration

Add one schema change as the next numbered migration.

## Steps

1. List `db/migrations/` and read the latest files. The next file is `V<n+1>__<snake_name>.sql`, zero-padded to three digits (e.g. `V002__add_products_price.sql`).
2. Write the SQL: plain Postgres DDL, one change per file.
3. Show the file name and SQL. Wait for approval before applying.
4. From `backend/`, run `uv run python -m app.migrate`, then `uv run pytest`. Fix failures in the new file only.
5. Report the file applied and the test result.

## Rules

- Additive changes use nullable columns (or a default), so code can roll back without the schema.
- Never edit a file that is already applied. Fix forward with a new file.
- Drops and renames take two deploys: first add and switch code over, then drop in a later migration.
