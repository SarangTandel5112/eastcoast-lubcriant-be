"""SQLAlchemy entity for the `product_applications` junction table."""

import uuid

from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ProductApplication(Base):
    __tablename__ = "product_applications"

    __table_args__ = (
        PrimaryKeyConstraint("product_id", "application_id"),
    )

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="product_applications")
    application = relationship("Application", back_populates="product_applications")
