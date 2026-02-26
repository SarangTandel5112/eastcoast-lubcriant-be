from app.common.schemas.base import BaseSchema
"""Order Domain Class Objects — internal typed representations for orders."""

from dataclasses import dataclass, field

from app.common.base_dco import BaseDCO

@dataclass
class OrderItemDCO:
    """A single line-item within an order."""
    product_id: str = ""
    quantity: int = 0
    price: float = 0.0

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItemDCO":
        return cls(
            product_id=data.get("product_id", ""),
            quantity=data.get("quantity", 0),
            price=data.get("price", 0.0),
        )

@dataclass
class ShippingAddressDCO:
    """Shipping address embedded in an order."""
    full_name: str = ""
    address_line1: str = ""
    address_line2: str | None = None
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ShippingAddressDCO":
        return cls(
            full_name=data.get("full_name", ""),
            address_line1=data.get("address_line1", ""),
            address_line2=data.get("address_line2"),
            city=data.get("city", ""),
            state=data.get("state", ""),
            postal_code=data.get("postal_code", ""),
            country=data.get("country", ""),
        )

@dataclass
class OrderDCO(BaseDCO):
    """Domain object for Order, used between controller ↔ service ↔ model."""
    user_id: str = ""
    items: list[OrderItemDCO] = field(default_factory=list)
    shipping_address: ShippingAddressDCO = field(default_factory=ShippingAddressDCO)
    status: str = "pending"
    total_amount: float = 0.0
    payment_intent_id: str | None = None

    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "shipping_address": self.shipping_address.to_dict(),
            "status": self.status,
            "total_amount": self.total_amount,
            "payment_intent_id": self.payment_intent_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderDCO":
        """Hydrate from a stored dict."""
        return cls(
            id=data.get("id", ""),
            user_id=data.get("user_id", ""),
            items=[OrderItemDCO.from_dict(i) for i in data.get("items", [])],
            shipping_address=ShippingAddressDCO.from_dict(data.get("shipping_address", {})),
            status=data.get("status", "pending"),
            total_amount=data.get("total_amount", 0.0),
            payment_intent_id=data.get("payment_intent_id"),
            created_at=data.get("created_at", ""),
        )
