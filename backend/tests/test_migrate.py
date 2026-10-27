import psycopg
import pytest

from app.migrate import DATABASE_URL, migrate


def test_migrate_is_idempotent(capsys):
    migrate()
    capsys.readouterr()

    migrate()

    assert capsys.readouterr().out == "up to date\n"
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute("SELECT filename FROM schema_migrations").fetchall()
    assert ("V001__create_products.sql",) in rows


def test_products_rejects_blank_name():
    migrate()
    with psycopg.connect(DATABASE_URL) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute("INSERT INTO products (name) VALUES ('   ')")
