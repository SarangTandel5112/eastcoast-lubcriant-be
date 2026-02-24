"""SQLAlchemy entity for the `product_variant_attributes` junction table."""

import uuid

from sqlalchemy import Column, Text, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ProductVariantAttribute(Base):
    __tablename__ = "product_variant_attributes"

    __table_args__ = (
        PrimaryKeyConstraint("variant_id", "attribute_id"),
    )

    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=False)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("attributes.id"), nullable=False)
    value = Column(Text, nullable=False)

    # Relationships
    variant = relationship("ProductVariant", back_populates="product_variant_attributes")
    attribute = relationship("Attribute", back_populates="product_variant_attributes")
