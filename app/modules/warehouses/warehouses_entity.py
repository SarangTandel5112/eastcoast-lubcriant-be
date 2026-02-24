"""SQLAlchemy entity for the `warehouses` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(Text, nullable=False)
    code = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    inventory = relationship("Inventory", back_populates="warehouse")
    inventory_movements = relationship("InventoryMovement", back_populates="warehouse")
