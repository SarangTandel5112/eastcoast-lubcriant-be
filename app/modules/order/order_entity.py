"""SQLAlchemy ORM entities for `orders` and `order_items` tables."""

import uuid

from sqlalchemy import String, Text, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.base_entity import Base, TimestampMixin


class OrderItemEntity(TimestampMixin, Base):
    """Represents a row in the `order_items` table."""

    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    def __repr__(self) -> str:
        return f"<OrderItemEntity id={self.id} order_id={self.order_id} product_id={self.product_id}>"


class OrderEntity(TimestampMixin, Base):
    """Represents a row in the `orders` table."""

    __tablename__ = "orders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Shipping address (flat columns)
    shipping_full_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    shipping_address_line1: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    shipping_address_line2: Mapped[str | None] = mapped_column(String(500), nullable=True)
    shipping_city: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    shipping_state: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    shipping_postal_code: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    shipping_country: Mapped[str] = mapped_column(String(100), nullable=False, default="")

    # Relationship to order items
    items: Mapped[list["OrderItemEntity"]] = relationship(
        "OrderItemEntity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<OrderEntity id={self.id} user_id={self.user_id} status={self.status}>"
