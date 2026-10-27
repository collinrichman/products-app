from contextlib import nullcontext

import pytest
from fastapi.testclient import TestClient

import app.main
from app.main import app as api

client = TestClient(api)


@pytest.fixture(autouse=True)
def fake_db(monkeypatch):
    """Replace the db layer with an in-memory list so tests never touch Postgres."""
    rows = []

    def create_product(conn, name):
        row = {"id": len(rows) + 1, "name": name}
        rows.append(row)
        return row

    monkeypatch.setattr(app.main, "get_conn", nullcontext)
    monkeypatch.setattr(app.main, "list_products", lambda conn: list(rows))
    monkeypatch.setattr(app.main, "create_product", create_product)
    return rows


def test_create_product_returns_201_and_row():
    response = client.post("/products", json={"name": "  Widget  "})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Widget"}


def test_list_products_returns_created_products():
    client.post("/products", json={"name": "P1"})

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "P1"}]


def test_create_product_rejects_blank_name(fake_db):
    response = client.post("/products", json={"name": "   "})

    assert response.status_code == 422
    assert "name must not be blank" in response.text
    assert fake_db == []


def test_create_product_requires_name():
    response = client.post("/products", json={})

    assert response.status_code == 422
