"""DCO for the orders table — WRITE operations."""

from uuid import UUID
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.modules.orders.orders_entity import OrderStatusEnum


class OrderDCO(BaseModel):
    dealer_id: UUID
    status: OrderStatusEnum
    currency: str = "CAD"
    shipping_address_snapshot: dict
    tax_amount: Decimal
    delivery_fee: Optional[Decimal] = None
    discount_amount: Decimal = Decimal("0")
    placed_at: Optional[str] = None


class OrderUpdateDCO(BaseModel):
    status: Optional[OrderStatusEnum] = None
    currency: Optional[str] = None
    shipping_address_snapshot: Optional[dict] = None
    delivery_fee: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
