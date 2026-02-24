"""Auth Domain Class Object — internal typed representation of a user."""

from dataclasses import dataclass

from app.common.base_dco import BaseDCO


@dataclass
class UserDCO(BaseDCO):
    """Domain object for User, used between controller ↔ service ↔ model."""
    name: str = ""
    email: str = ""
    password: str = ""  # hashed
    role: str = "customer"

    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserDCO":
        """Hydrate from a stored dict."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=data.get("role", "customer"),
            created_at=data.get("created_at", ""),
        )
