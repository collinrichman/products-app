import psycopg
import pytest
from psycopg.rows import dict_row

from app.db import DATABASE_URL, seed_products
from app.seed import PRODUCT_NAMES


@pytest.fixture
def conn():
    """Real Postgres connection, rolled back after the test."""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn
        conn.rollback()


def test_product_names_are_unique_and_share_prefixes():
    assert len(PRODUCT_NAMES) >= 300
    assert len(set(PRODUCT_NAMES)) == len(PRODUCT_NAMES)
    assert sum(name.startswith("Screw") for name in PRODUCT_NAMES) >= 20


def test_seed_products_inserts_each_name_once(conn):
    seed_products(conn, PRODUCT_NAMES)
    inserted_again = seed_products(conn, PRODUCT_NAMES)

    counts = conn.execute(
        "SELECT name, count(*) AS n FROM products WHERE name = ANY(%s) GROUP BY name",
        (PRODUCT_NAMES,),
    ).fetchall()

    assert inserted_again == 0
    assert len(counts) == len(PRODUCT_NAMES)
    assert all(row["n"] == 1 for row in counts)
