"""SQLAlchemy entity for the `inventory_movements` table."""

import uuid
from uuid import uuid4
from enum import Enum as PyEnum

from sqlalchemy import Column, Text, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class MovementTypeEnum(str, PyEnum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    movement_type = Column(Enum(MovementTypeEnum), nullable=False)
    quantity = Column(Integer, nullable=False)
    reference_type = Column(Text, nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    variant = relationship("ProductVariant", back_populates="inventory_movements")
    warehouse = relationship("Warehouse", back_populates="inventory_movements")
