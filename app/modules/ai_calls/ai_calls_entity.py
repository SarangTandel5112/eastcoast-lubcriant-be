"""SQLAlchemy entity for the `ai_calls` table."""

import uuid
from uuid import uuid4
from enum import Enum as PyEnum

from sqlalchemy import Column, Text, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class CallStatusEnum(str, PyEnum):
    INITIATED = "INITIATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AiCall(Base):
    __tablename__ = "ai_calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    dealer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    call_status = Column(Enum(CallStatusEnum), nullable=False)
    provider_call_id = Column(Text, nullable=True)
    call_summary = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    call_duration_sec = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dealer = relationship("User", back_populates="ai_calls")
