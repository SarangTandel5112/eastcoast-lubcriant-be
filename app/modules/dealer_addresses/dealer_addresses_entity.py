"""SQLAlchemy entity for the `dealer_addresses` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class DealerAddress(Base):
    __tablename__ = "dealer_addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    dealer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    address_line1 = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    province = Column(Text, nullable=False)
    postal_code = Column(Text, nullable=False)
    country = Column(Text, nullable=False)
    label = Column(Text, nullable=True)
    address_line2 = Column(Text, nullable=True)
    is_default = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    dealer = relationship("User", back_populates="dealer_addresses")
