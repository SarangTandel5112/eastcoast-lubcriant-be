"""DTO for the orders table — READ operations."""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.common.schemas.base import BaseSchema
from app.modules.orders.orders_entity import OrderStatusEnum

class OrderDTO(BaseSchema):

    id: UUID
    dealer_id: UUID
    status: OrderStatusEnum
    currency: str
    shipping_address_snapshot: dict
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    order_number: Optional[str] = None
    delivery_fee: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    placed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
