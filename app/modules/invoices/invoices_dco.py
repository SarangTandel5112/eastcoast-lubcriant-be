"""DCO for the invoices table — WRITE operations."""

from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

from app.common.schemas.base import BaseSchema

class InvoiceDCO(BaseSchema):
    order_id: UUID
    invoice_number: str
    gst_amount: Optional[Decimal] = None
    pst_amount: Optional[Decimal] = None
    hst_amount: Optional[Decimal] = None
    pdf_url: Optional[str] = None
    issued_at: Optional[datetime] = None

class InvoiceUpdateDCO(BaseSchema):
    invoice_number: Optional[str] = None
    gst_amount: Optional[Decimal] = None
    pst_amount: Optional[Decimal] = None
    hst_amount: Optional[Decimal] = None
    pdf_url: Optional[str] = None
    issued_at: Optional[datetime] = None
