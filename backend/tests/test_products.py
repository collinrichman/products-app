from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_product_returns_201_and_row():
    response = client.post("/products", json={"name": "  Widget  "})

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["name"] == "Widget"


def test_list_products_includes_created_product():
    created = client.post("/products", json={"name": "Gadget"}).json()

    response = client.get("/products")

    assert response.status_code == 200
    assert created in response.json()


def test_create_product_rejects_blank_name():
    response = client.post("/products", json={"name": "   "})

    assert response.status_code == 422
    assert "name must not be blank" in response.text


def test_create_product_requires_name():
    response = client.post("/products", json={})

    assert response.status_code == 422
