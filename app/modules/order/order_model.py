from datetime import datetime, timezone
from typing import Optional

from app.modules.order.order_dco import OrderDCO, OrderItemDCO, ShippingAddressDCO


# ── In-memory store (replace with real DB later) ─────────
_orders_db: dict[str, dict] = {}
_order_counter: int = 0


def create_order(dco: OrderDCO) -> OrderDCO:
    """Persist a new order and return the hydrated DCO with generated id."""
    global _order_counter
    _order_counter += 1
    order_id = f"order_{_order_counter}"

    dco.id = order_id
    dco.created_at = datetime.now(timezone.utc).isoformat()

    _orders_db[order_id] = dco.to_dict()
    return dco


def find_order_by_id(order_id: str) -> Optional[OrderDCO]:
    data = _orders_db.get(order_id)
    if data is None:
        return None
    return OrderDCO.from_dict(data)


def get_orders_by_user(user_id: str) -> list[OrderDCO]:
    return [
        OrderDCO.from_dict(o)
        for o in _orders_db.values()
        if o["user_id"] == user_id
    ]


def update_order_status(order_id: str, new_status: str) -> Optional[OrderDCO]:
    order = _orders_db.get(order_id)
    if not order:
        return None

    order["status"] = new_status
    _orders_db[order_id] = order
    return OrderDCO.from_dict(order)
