from contextlib import nullcontext

import pytest
from fastapi.testclient import TestClient

import app.main
from app.main import app as api
from app.trie import ProductTrie

client = TestClient(api)


@pytest.fixture(autouse=True)
def fake_db(monkeypatch):
    """Replace the db layer with an in-memory list so tests never touch Postgres."""
    rows = []

    def create_product(conn, name, popularity):
        row = {"id": len(rows) + 1, "name": name, "popularity": popularity}
        rows.append(row)
        return row

    monkeypatch.setattr(app.main, "get_conn", nullcontext)
    monkeypatch.setattr(app.main, "list_products", lambda conn: list(rows))
    monkeypatch.setattr(app.main, "create_product", create_product)
    monkeypatch.setattr(app.main, "product_trie", ProductTrie())
    return rows


def test_create_product_returns_201_and_row():
    response = client.post("/products", json={"name": "  Widget  "})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Widget", "popularity": 0}


def test_create_product_accepts_popularity():
    response = client.post("/products", json={"name": "Widget", "popularity": 7})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Widget", "popularity": 7}


def test_list_products_returns_created_products():
    client.post("/products", json={"name": "P1"})

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "P1", "popularity": 0}]


def test_create_product_rejects_blank_name(fake_db):
    response = client.post("/products", json={"name": "   "})

    assert response.status_code == 422
    assert "name must not be blank" in response.text
    assert fake_db == []


def test_create_product_requires_name():
    response = client.post("/products", json={})

    assert response.status_code == 422


def test_search_returns_created_products_by_prefix_most_popular_first():
    client.post("/products", json={"name": "Hand Saw", "popularity": 2})
    client.post("/products", json={"name": "Hammer", "popularity": 5})
    client.post("/products", json={"name": "Drill", "popularity": 9})

    response = client.get("/products/search", params={"prefix": "Ha"})

    assert response.status_code == 200
    assert [p["name"] for p in response.json()] == ["Hammer", "Hand Saw"]


def test_search_returns_empty_list_without_match_or_prefix():
    client.post("/products", json={"name": "Hammer"})

    assert client.get("/products/search", params={"prefix": "x"}).json() == []
    assert client.get("/products/search").json() == []


def test_startup_loads_existing_products_into_search(fake_db):
    fake_db.append({"id": 1, "name": "Hammer", "popularity": 5})

    with TestClient(api) as started:
        response = started.get("/products/search", params={"prefix": "ham"})

    assert response.json() == [{"id": 1, "name": "Hammer", "popularity": 5}]
