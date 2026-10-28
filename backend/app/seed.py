"""Seed local dev data: product names in shared-prefix families for type-ahead testing."""

from app.db import get_conn, seed_products

ITEMS = [
    "Bolt", "Bolt Cutter", "Bracket", "Brad Nail",
    "Clamp", "Clamp Meter",
    "Drill", "Drill Bit", "Driver",
    "Glove", "Glue",
    "Hammer", "Hammer Drill", "Hand Saw", "Hand Truck",
    "Pipe", "Pipe Wrench", "Pliers", "Plug",
    "Sander", "Sandpaper", "Saw Blade",
    "Screw", "Screw Anchor", "Screwdriver",
    "Washer", "Wire", "Wire Stripper", "Wrench", "Wrench Set",
]  # fmt: skip
VARIANTS = [
    "Standard", "Heavy Duty", "Compact", "Pro", "Mini",
    "XL", "Steel", "Stainless", "Brass", "Kit",
]  # fmt: skip

PRODUCT_NAMES = [f"{item} {variant}" for item in ITEMS for variant in VARIANTS]


def seed() -> None:
    with get_conn() as conn:
        inserted = seed_products(conn, PRODUCT_NAMES)
    print(f"seeded {inserted} of {len(PRODUCT_NAMES)} products")


if __name__ == "__main__":
    seed()
