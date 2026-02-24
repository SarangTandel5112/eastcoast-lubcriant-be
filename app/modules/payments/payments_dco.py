"""DCO for the payments table — WRITE operations."""

from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.modules.payments.payments_entity import PaymentStatusEnum


class PaymentDCO(BaseModel):
    order_id: UUID
    stripe_payment_id: str
    payment_method: str
    status: PaymentStatusEnum
    amount: Decimal
    currency: str
    paid_at: Optional[datetime] = None


class PaymentUpdateDCO(BaseModel):
    status: Optional[PaymentStatusEnum] = None
    paid_at: Optional[datetime] = None
