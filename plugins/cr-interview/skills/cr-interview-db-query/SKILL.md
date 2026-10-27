---
name: cr-interview-db-query
description: Use when the user asks to "query the database", "how many products", "what's in the db", or asks a question the data answers. Answers it with read-only SQL against the local Postgres.
---

# DB Query

Answer a question about the data with read-only SQL.

## Steps

1. Load the schema. Set `URL=postgresql://products:products@localhost:5432/products` (or `$DATABASE_URL`) and run, with `PGOPTIONS='-c default_transaction_read_only=on'` on every `psql` call:
   - `psql "$URL" -c '\dt'`, then `psql "$URL" -c '\d <table>'` per table.
   - `SELECT count(*)` per table.
   - `SELECT filename, applied_at FROM schema_migrations ORDER BY filename`.
2. Write SQL for the question using only the columns that exist.
3. Run it: `PGOPTIONS='-c default_transaction_read_only=on' psql "$URL" -c '<sql>'`.
4. Answer with the SQL and a short interpretation of the result.

## Rules

- Read only. Never run INSERT, UPDATE, DELETE, or DDL, even if asked; point to `cr-interview-db-migration` for schema changes.
