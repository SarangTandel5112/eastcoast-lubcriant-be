"""SQLAlchemy entity for the `standards` table."""

import uuid
from uuid import uuid4
from enum import Enum as PyEnum

from sqlalchemy import Column, Text, String, DateTime, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class StandardTypeEnum(str, PyEnum):
    API = "API"
    ACEA = "ACEA"
    OEM = "OEM"
    ILSAC = "ILSAC"
    JASO = "JASO"
    ISO = "ISO"


class Standard(Base):
    __tablename__ = "standards"

    __table_args__ = (
        UniqueConstraint("name", "standard_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(Text, nullable=False)
    standard_type = Column(Enum(StandardTypeEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product_variant_standards = relationship("ProductVariantStandard", back_populates="standard")
