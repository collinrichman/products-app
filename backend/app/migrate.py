from pathlib import Path

import psycopg

from app.db import DATABASE_URL

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "db" / "migrations"


def migrate() -> None:
    """Apply each unapplied db/migrations/V*.sql in order, one transaction per file."""
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " filename TEXT PRIMARY KEY,"
            " applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        applied = {row[0] for row in conn.execute("SELECT filename FROM schema_migrations")}
        pending = [p for p in sorted(MIGRATIONS_DIR.glob("V*.sql")) if p.name not in applied]

        for path in pending:
            with conn.transaction():
                conn.execute(path.read_text())
                conn.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", (path.name,))
            print(f"applied {path.name}")

        if not pending:
            print("up to date")


if __name__ == "__main__":
    migrate()
