"""SQLAlchemy entity for the `applications` table."""

import uuid
from uuid import uuid4

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(Text, nullable=False, unique=True)

    # Relationships
    product_applications = relationship("ProductApplication", back_populates="application")
