"""DTO for the invoices table — READ operations."""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InvoiceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    invoice_number: str
    gst_amount: Optional[Decimal] = None
    pst_amount: Optional[Decimal] = None
    hst_amount: Optional[Decimal] = None
    pdf_url: Optional[str] = None
    issued_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
