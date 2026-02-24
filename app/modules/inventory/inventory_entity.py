"""SQLAlchemy entity for the `inventory` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint("variant_id", "warehouse_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    reserved_quantity = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    variant = relationship("ProductVariant", back_populates="inventory")
    warehouse = relationship("Warehouse", back_populates="inventory")
