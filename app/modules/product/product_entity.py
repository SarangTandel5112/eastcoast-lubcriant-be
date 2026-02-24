"""SQLAlchemy ORM entity for the `products` table."""

import uuid

from sqlalchemy import String, Text, Float, Integer, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_entity import Base, TimestampMixin


class ProductEntity(TimestampMixin, Base):
    """Represents a row in the `products` table."""

    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    images: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=[])
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=[])
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ProductEntity id={self.id} name={self.name}>"
