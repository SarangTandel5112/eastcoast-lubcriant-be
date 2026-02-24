"""SQLAlchemy entity for the `product_variant_standards` junction table."""

import uuid

from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ProductVariantStandard(Base):
    __tablename__ = "product_variant_standards"

    __table_args__ = (
        PrimaryKeyConstraint("variant_id", "standard_id"),
    )

    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    standard_id = Column(UUID(as_uuid=True), ForeignKey("standards.id"), nullable=False)

    # Relationships
    variant = relationship("ProductVariant", back_populates="product_variant_standards")
    standard = relationship("Standard", back_populates="product_variant_standards")
