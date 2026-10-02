"""Seeded product/order/customer generator for the thilimcp shop.

A small, deterministic (seed=42) e-commerce backend: ~30 products across three categories, each
with its own return window (electronics 15 days, clothing 30 days, perishables non-returnable),
40 customers, 150 orders, and their line items. Customer #1 is always "Priya Shah" with three
explicit orders, and order #123 is guaranteed to exist — both lean on by the course's lessons.
"""
import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

RETURN_WINDOWS = {"electronics": 15, "clothing": 30, "perishables": 0}
PRODUCT_NAMES = {
    "electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Laptop Stand", "USB-C Hub",
                    "Webcam", "Mechanical Keyboard", "Portable SSD", "Smart Watch",
                    "Noise-Canceling Headphones", "Phone Charger"],
    "clothing": ["Cotton T-Shirt", "Denim Jacket", "Running Shoes", "Wool Sweater",
                 "Rain Jacket", "Linen Shirt", "Hiking Boots", "Fleece Hoodie",
                 "Canvas Sneakers", "Wind Breaker"],
    "perishables": ["Artisan Coffee Beans", "Organic Honey", "Dark Chocolate Box",
                     "Fresh Pasta", "Spice Gift Set", "Herbal Tea Sampler",
                     "Gourmet Cheese", "Dried Fruit Mix", "Olive Oil", "Specialty Jam"],
}
STATUSES = ["placed", "shipped", "delivered", "returned"]


def seed_shop(db_path: str = "shop.db") -> sqlite3.Connection:
    """Create and seed the shop database at db_path, overwriting any existing file."""
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text())

    random.seed(42)
    Faker.seed(42)
    fake = Faker()

    product_id = 1
    for category, names in PRODUCT_NAMES.items():
        for name in names:
            conn.execute(
                "INSERT INTO products (id, name, category, price_cents, return_window_days) "
                "VALUES (?,?,?,?,?)",
                (product_id, name, category, random.randint(999, 29999), RETURN_WINDOWS[category]),
            )
            product_id += 1
    n_products = product_id - 1

    # Customer #1 is deliberately Priya Shah, not random — "list her orders" needs a stable answer.
    conn.execute(
        "INSERT INTO customers (id, name, email) VALUES (1, 'Priya Shah', 'priya.shah@example.com')"
    )
    for cid in range(2, 41):
        conn.execute("INSERT INTO customers (id, name, email) VALUES (?,?,?)", (cid, fake.name(), fake.email()))
    n_customers = 40

    def random_order_date():
        days_ago = random.randint(0, 60)
        return (datetime(2026, 9, 30) - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    order_id = 1
    item_id = 1

    # Priya Shah gets 3 explicit orders first.
    for _ in range(3):
        conn.execute("INSERT INTO orders (id, customer_id, created_at, status) VALUES (?,?,?,?)",
                     (order_id, 1, random_order_date(), random.choice(STATUSES)))
        for _ in range(random.randint(1, 2)):
            conn.execute("INSERT INTO order_items (id, order_id, product_id, quantity) VALUES (?,?,?,?)",
                         (item_id, order_id, random.randint(1, n_products), random.randint(1, 3)))
            item_id += 1
        order_id += 1

    # 150 orders total — guarantees order #123 is real.
    while order_id <= 150:
        cid = random.randint(1, n_customers)
        conn.execute("INSERT INTO orders (id, customer_id, created_at, status) VALUES (?,?,?,?)",
                     (order_id, cid, random_order_date(), random.choice(STATUSES)))
        for _ in range(random.randint(1, 3)):
            conn.execute("INSERT INTO order_items (id, order_id, product_id, quantity) VALUES (?,?,?,?)",
                         (item_id, order_id, random.randint(1, n_products), random.randint(1, 3)))
            item_id += 1
        order_id += 1

    conn.commit()
    return conn


if __name__ == "__main__":
    conn = seed_shop()
    for table in ["products", "customers", "orders", "order_items"]:
        n = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"{table}: {n} rows")
