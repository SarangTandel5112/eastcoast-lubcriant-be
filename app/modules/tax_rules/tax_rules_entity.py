"""SQLAlchemy entity for the `tax_rules` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Text, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base


class TaxRule(Base):
    __tablename__ = "tax_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    province = Column(Text, nullable=False, unique=True)
    gst_rate = Column(Numeric(5, 2), nullable=False)
    pst_rate = Column(Numeric(5, 2), nullable=True)
    hst_rate = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
