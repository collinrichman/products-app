import os

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://products:products@localhost:5432/products"
)


def get_conn() -> psycopg.Connection[dict]:
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def list_products(conn: psycopg.Connection[dict]) -> list[dict]:
    return conn.execute("SELECT id, name FROM products ORDER BY id").fetchall()


def create_product(conn: psycopg.Connection[dict], name: str) -> dict:
    return conn.execute(
        "INSERT INTO products (name) VALUES (%s) RETURNING id, name", (name,)
    ).fetchone()
