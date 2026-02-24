"""SQLAlchemy ORM entity for the `users` table."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_entity import Base, TimestampMixin


class UserEntity(TimestampMixin, Base):
    """Represents a row in the `users` table."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="customer")

    def __repr__(self) -> str:
        return f"<UserEntity id={self.id} email={self.email} role={self.role}>"
