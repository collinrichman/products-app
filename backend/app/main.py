import logging

from fastapi import FastAPI

from app.db import create_product, get_conn, list_products
from app.models import Product, ProductCreate

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="Products")


@app.get("/products", response_model=list[Product])
def get_products() -> list[dict]:
    with get_conn() as conn:
        products = list_products(conn)
    log.info("listed %d products", len(products))
    return products


@app.post("/products", response_model=Product, status_code=201)
def post_product(body: ProductCreate) -> dict:
    with get_conn() as conn:
        product = create_product(conn, body.name)
    log.info("created product id=%d", product["id"])
    return product
