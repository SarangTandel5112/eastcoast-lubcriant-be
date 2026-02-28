from __future__ import annotations
"""ORM Entity for the `users` table."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_entity import Base, TimestampMixin


class RoleEnum(str, enum.Enum):
    """Available user roles."""
    ADMIN = "ADMIN"
    DEALER = "DEALER"


class User(Base, TimestampMixin):
    """User entity for authentication and profile management."""
    
    __tablename__ = "users"

    role: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default=RoleEnum.DEALER,
        comment="ADMIN, DEALER"
    )
    business_name: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        Text, 
        nullable=False, 
        unique=True, 
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    province: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    contact_name: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    phone: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True, 
        index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        server_default="true"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    current_refresh_jti: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True, 
        comment="Stores JWT refresh token ID to support revoking sessions"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # ── Relationships ──────────────────────────────────────────
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="dealer", cascade="all, delete-orphan"
    )
    dealer_addresses: Mapped[list["DealerAddress"]] = relationship(
        "DealerAddress", back_populates="dealer", cascade="all, delete-orphan"
    )
    ai_calls: Mapped[list["AiCall"]] = relationship(
        "AiCall", back_populates="dealer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(email='{self.email}', role='{self.role}')>"
