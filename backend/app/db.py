import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://products:products@localhost:5432/products"
)
