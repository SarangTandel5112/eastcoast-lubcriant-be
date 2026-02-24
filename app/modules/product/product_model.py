from datetime import datetime, timezone
from typing import Optional

from app.modules.product.product_dco import ProductDCO


# ── In-memory store (replace with real DB later) ─────────
_products_db: dict[str, dict] = {}
_product_counter: int = 0


def create_product(dco: ProductDCO) -> ProductDCO:
    """Persist a new product and return the hydrated DCO with generated id."""
    global _product_counter
    _product_counter += 1
    product_id = f"prod_{_product_counter}"

    dco.id = product_id
    dco.created_at = datetime.now(timezone.utc).isoformat()

    _products_db[product_id] = dco.to_dict()
    return dco


def find_product_by_id(product_id: str) -> Optional[ProductDCO]:
    data = _products_db.get(product_id)
    if data is None:
        return None
    return ProductDCO.from_dict(data)


def get_all_products(category: Optional[str] = None, search: Optional[str] = None) -> list[ProductDCO]:
    products = list(_products_db.values())

    if category:
        products = [p for p in products if p.get("category") == category]
    if search:
        products = [p for p in products if search.lower() in p.get("name", "").lower()]

    return [ProductDCO.from_dict(p) for p in products]


def update_product(product_id: str, update_data: dict) -> Optional[ProductDCO]:
    product = _products_db.get(product_id)
    if not product:
        return None

    updated = {**product, **update_data}
    _products_db[product_id] = updated
    return ProductDCO.from_dict(updated)


def delete_product(product_id: str) -> bool:
    if product_id not in _products_db:
        return False
    del _products_db[product_id]
    return True
