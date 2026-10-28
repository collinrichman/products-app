import psycopg

from app.db import DATABASE_URL


def test_products_rejects_blank_name():
    with psycopg.connect(DATABASE_URL) as conn:
        checks = conn.execute(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint"
            " WHERE conrelid = 'products'::regclass AND contype = 'c'"
        ).fetchall()

    assert ("CHECK ((length(TRIM(BOTH FROM name)) > 0))",) in checks


def test_products_popularity_defaults_to_zero():
    with psycopg.connect(DATABASE_URL) as conn:
        column = conn.execute(
            "SELECT data_type, is_nullable, column_default FROM information_schema.columns"
            " WHERE table_name = 'products' AND column_name = 'popularity'"
        ).fetchone()

    assert column == ("integer", "NO", "0")
