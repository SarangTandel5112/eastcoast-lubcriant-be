from datetime import datetime, timezone
from typing import Optional


# ── In-memory store (replace with real DB later) ─────────
_orders_db: dict[str, dict] = {}
_order_counter: int = 0


def create_order(user_id: str, items: list[dict], shipping_address: dict,
                 total_amount: float, payment_method: str) -> dict:
    global _order_counter
    _order_counter += 1
    order_id = f"order_{_order_counter}"

    order = {
        "id": order_id,
        "user_id": user_id,
        "items": items,
        "shipping_address": shipping_address,
        "status": "pending",
        "total_amount": total_amount,
        "payment_intent_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _orders_db[order_id] = order
    return order


def find_order_by_id(order_id: str) -> Optional[dict]:
    return _orders_db.get(order_id)


def get_orders_by_user(user_id: str) -> list[dict]:
    return [o for o in _orders_db.values() if o["user_id"] == user_id]


def update_order_status(order_id: str, new_status: str) -> Optional[dict]:
    order = _orders_db.get(order_id)
    if not order:
        return None

    order["status"] = new_status
    _orders_db[order_id] = order
    return order
