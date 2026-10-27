import psycopg
import pytest

from app.db import DATABASE_URL


def test_products_rejects_blank_name():
    with psycopg.connect(DATABASE_URL) as conn:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction(force_rollback=True):
            conn.execute("INSERT INTO products (name) VALUES ('   ')")
