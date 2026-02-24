"""SQLAlchemy entity for the `product_variants` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Text, String, Boolean, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    sku = Column(Text, nullable=False, unique=True)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="CAD")
    moq = Column(Integer, nullable=False, default=1)
    barcode = Column(Text, nullable=True)
    pack_size = Column(Text, nullable=True)
    weight_kg = Column(Numeric(10, 3), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="variants")
    variant_images = relationship("VariantImage", back_populates="variant")
    product_variant_standards = relationship("ProductVariantStandard", back_populates="variant")
    product_variant_attributes = relationship("ProductVariantAttribute", back_populates="variant")
    inventory = relationship("Inventory", back_populates="variant")
    inventory_movements = relationship("InventoryMovement", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")
