"""SQLAlchemy entity for the `invoices` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, unique=True)
    invoice_number = Column(Text, nullable=False, unique=True)
    gst_amount = Column(Numeric(12, 2), nullable=True)
    pst_amount = Column(Numeric(12, 2), nullable=True)
    hst_amount = Column(Numeric(12, 2), nullable=True)
    pdf_url = Column(Text, nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships (One-to-One with Order)
    order = relationship("Order", back_populates="invoice", uselist=False)
