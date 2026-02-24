"""Order DTOs — request & response Pydantic models for the Order API."""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from app.modules.order.order_dco import OrderDCO, OrderItemDCO, ShippingAddressDCO


class OrderStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


# ── Request DTOs ─────────────────────────────────────────────

class OrderItemRequestDTO(BaseModel):
    """DTO for a single order line-item in a request."""
    product_id: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)  # price at time of order


class ShippingAddressRequestDTO(BaseModel):
    """DTO for shipping address in a request."""
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str


class CreateOrderRequestDTO(BaseModel):
    """DTO for creating a new order."""
    items: List[OrderItemRequestDTO]
    shipping_address: ShippingAddressRequestDTO
    payment_method: str = "stripe"
    coupon_code: Optional[str] = None


# ── Response DTOs ────────────────────────────────────────────

class OrderItemResponseDTO(BaseModel):
    """DTO for a single order line-item in a response."""
    product_id: str
    quantity: int
    price: float


class ShippingAddressResponseDTO(BaseModel):
    """DTO for shipping address in a response."""
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str


class OrderResponseDTO(BaseModel):
    """DTO returned for a single order."""
    id: str
    user_id: str
    items: List[OrderItemResponseDTO]
    shipping_address: ShippingAddressResponseDTO
    status: OrderStatusEnum
    total_amount: float
    payment_intent_id: Optional[str] = None
    created_at: str

    @classmethod
    def from_dco(cls, dco: OrderDCO) -> "OrderResponseDTO":
        """Build a response DTO from an order DCO."""
        return cls(
            id=dco.id,
            user_id=dco.user_id,
            items=[
                OrderItemResponseDTO(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in dco.items
            ],
            shipping_address=ShippingAddressResponseDTO(
                full_name=dco.shipping_address.full_name,
                address_line1=dco.shipping_address.address_line1,
                address_line2=dco.shipping_address.address_line2,
                city=dco.shipping_address.city,
                state=dco.shipping_address.state,
                postal_code=dco.shipping_address.postal_code,
                country=dco.shipping_address.country,
            ),
            status=dco.status,
            total_amount=dco.total_amount,
            payment_intent_id=dco.payment_intent_id,
            created_at=dco.created_at,
        )
