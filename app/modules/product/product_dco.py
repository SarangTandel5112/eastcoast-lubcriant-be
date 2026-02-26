from app.common.schemas.base import BaseSchema
"""Product Domain Class Object — internal typed representation of a product."""

from dataclasses import dataclass, field

from app.common.base_dco import BaseDCO

@dataclass
class ProductDCO(BaseDCO):
    """Domain object used between controller ↔ service ↔ model layers."""
    name: str = ""
    description: str = ""
    price: float = 0.0
    stock: int = 0
    category: str = ""
    images: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_by: str = ""

    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "images": self.images,
            "tags": self.tags,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProductDCO":
        """Hydrate from a stored dict."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            price=data.get("price", 0.0),
            stock=data.get("stock", 0),
            category=data.get("category", ""),
            images=data.get("images", []),
            tags=data.get("tags", []),
            created_by=data.get("created_by", ""),
            created_at=data.get("created_at", ""),
        )
