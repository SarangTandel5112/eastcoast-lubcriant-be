"""SQLAlchemy entity for the `order_items` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Text, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    sku_snapshot = Column(Text, nullable=True)
    name_snapshot = Column(Text, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")
