import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_product, get_conn, list_products
from app.models import Product, ProductCreate
from app.trie import ProductTrie

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

product_trie = ProductTrie()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_conn() as conn:
        products = list_products(conn)
    for product in products:
        product_trie.insert(product)
    log.info("indexed %d products for search", len(products))
    yield


app = FastAPI(title="Products", lifespan=lifespan)


@app.get("/products", response_model=list[Product])
def get_products() -> list[dict]:
    with get_conn() as conn:
        products = list_products(conn)
    log.info("listed %d products", len(products))
    return products


@app.get("/products/search", response_model=list[Product])
def search_products(prefix: str = "") -> list[dict]:
    return product_trie.search(prefix)


@app.post("/products", response_model=Product, status_code=201)
def post_product(body: ProductCreate) -> dict:
    with get_conn() as conn:
        product = create_product(conn, body.name, body.popularity)
    product_trie.insert(product)
    log.info("created product id=%d", product["id"])
    return product
