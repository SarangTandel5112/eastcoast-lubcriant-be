from datetime import datetime, timezone
from typing import Optional


# ── In-memory store (replace with real DB later) ─────────
_products_db: dict[str, dict] = {}
_product_counter: int = 0


def create_product(data: dict, admin_id: str) -> dict:
    global _product_counter
    _product_counter += 1
    product_id = f"prod_{_product_counter}"

    product = {
        "id": product_id,
        **data,
        "created_by": admin_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _products_db[product_id] = product
    return product


def find_product_by_id(product_id: str) -> Optional[dict]:
    return _products_db.get(product_id)


def get_all_products(category: Optional[str] = None, search: Optional[str] = None) -> list[dict]:
    products = list(_products_db.values())

    if category:
        products = [p for p in products if p.get("category") == category]
    if search:
        products = [p for p in products if search.lower() in p.get("name", "").lower()]

    return products


def update_product(product_id: str, update_data: dict) -> Optional[dict]:
    product = _products_db.get(product_id)
    if not product:
        return None

    updated = {**product, **update_data}
    _products_db[product_id] = updated
    return updated


def delete_product(product_id: str) -> bool:
    if product_id not in _products_db:
        return False
    del _products_db[product_id]
    return True
