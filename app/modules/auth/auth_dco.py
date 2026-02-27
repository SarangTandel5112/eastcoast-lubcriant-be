from app.common.schemas.base import BaseSchema
"""Auth Domain Class Object — internal typed representation of a user."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.common.base_dco import BaseDCO

@dataclass
class UserDCO(BaseDCO):
    """Domain object for User, used between route ↔ service ↔ model."""

    role: str = "DEALER"
    business_name: str = ""
    email: str = ""
    password_hash: str = ""
    province: str = ""
    contact_name: str | None = None
    phone: str | None = None
    is_active: bool = True
    last_login_at: str | None = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    deleted_at: str | None = None

    # Internal auth state (not exposed in response DTOs)
    current_refresh_jti: str | None = None

    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "id": self.id,
            "role": self.role,
            "business_name": self.business_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "province": self.province,
            "contact_name": self.contact_name,
            "phone": self.phone,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
            "current_refresh_jti": self.current_refresh_jti,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserDCO":
        """Hydrate from a stored dict."""
        return cls(
            id=data.get("id", ""),
            role=data.get("role", "DEALER"),
            business_name=data.get("business_name", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            province=data.get("province", ""),
            contact_name=data.get("contact_name"),
            phone=data.get("phone"),
            is_active=data.get("is_active", True),
            last_login_at=data.get("last_login_at"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            deleted_at=data.get("deleted_at"),
            current_refresh_jti=data.get("current_refresh_jti"),
        )
