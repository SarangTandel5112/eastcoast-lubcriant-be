"""SQLAlchemy entity for the `users` table."""

import uuid
from uuid import uuid4
from enum import Enum as PyEnum

from sqlalchemy import Column, Text, String, Boolean, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class RoleEnum(str, PyEnum):
    ADMIN = "ADMIN"
    DEALER = "DEALER"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    role = Column(Enum(RoleEnum), nullable=False)
    business_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    province = Column(Text, nullable=False)
    contact_name = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Internal auth field (not in DBML, required by auth module for JWT rotation)
    current_refresh_jti = Column(Text, nullable=True)

    # Relationships
    dealer_addresses = relationship("DealerAddress", back_populates="dealer")
    orders = relationship("Order", back_populates="dealer")
    ai_calls = relationship("AiCall", back_populates="dealer")
