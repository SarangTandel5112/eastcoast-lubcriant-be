"""Shared SQLAlchemy Base class used by all entities."""

from app.common.base_entity import Base, TimestampMixin

__all__ = ["Base", "TimestampMixin"]
