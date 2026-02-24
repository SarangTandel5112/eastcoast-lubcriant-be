"""DTO for the payments table — READ operations."""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.payments.payments_entity import PaymentStatusEnum


class PaymentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    stripe_payment_id: str
    payment_method: str
    status: PaymentStatusEnum
    amount: Decimal
    currency: str
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
