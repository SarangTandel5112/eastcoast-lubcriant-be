"""SQLAlchemy entity for the `attributes` table."""

import uuid
from uuid import uuid4
from enum import Enum as PyEnum

from sqlalchemy import Column, Text, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class DataTypeEnum(str, PyEnum):
    string = "string"
    number = "number"


class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(Text, nullable=False, unique=True)
    data_type = Column(Enum(DataTypeEnum), nullable=False)
    unit = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product_variant_attributes = relationship("ProductVariantAttribute", back_populates="attribute")
