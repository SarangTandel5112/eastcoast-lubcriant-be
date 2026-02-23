from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class OrderStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class OrderItemSchema(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)  # price at time of order


class ShippingAddressSchema(BaseModel):
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str


class CreateOrderSchema(BaseModel):
    items: List[OrderItemSchema]
    shipping_address: ShippingAddressSchema
    payment_method: str = "stripe"
    coupon_code: Optional[str] = None


class OrderResponseSchema(BaseModel):
    id: str
    user_id: str
    items: List[OrderItemSchema]
    shipping_address: ShippingAddressSchema
    status: OrderStatusEnum
    total_amount: float
    payment_intent_id: Optional[str] = None
    created_at: str
