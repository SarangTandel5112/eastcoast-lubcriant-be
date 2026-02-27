"""Product DTOs — request & response Pydantic models for the Product API."""

from pydantic import Field
from app.common.schemas.base import BaseSchema
from typing import Optional, List
from enum import Enum

from app.modules.product.product_dco import ProductDCO

class CategoryEnum(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    books = "books"
    other = "other"

# ── Request DTOs ─────────────────────────────────────────────

class CreateProductRequestDTO(BaseSchema):
    """DTO for creating a new product."""
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: CategoryEnum
    images: List[str] = []
    tags: List[str] = []

class UpdateProductRequestDTO(BaseSchema):
    """DTO for updating an existing product (all fields optional)."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[CategoryEnum] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None

# ── Response DTOs ────────────────────────────────────────────

class ProductResponseDTO(BaseSchema):
    """DTO returned for a single product."""
    id: str
    name: str
    description: str
    price: float
    stock: int
    category: str
    images: List[str]
    tags: List[str]
    created_by: str = ""
    created_at: str = ""

    @classmethod
    def from_dco(cls, dco: ProductDCO) -> "ProductResponseDTO":
        """Build a response DTO from a product DCO."""
        return cls(
            id=dco.id,
            name=dco.name,
            description=dco.description,
            price=dco.price,
            stock=dco.stock,
            category=dco.category,
            images=dco.images,
            tags=dco.tags,
            created_by=dco.created_by,
            created_at=dco.created_at,
        )

class ProductListResponseDTO(BaseSchema):
    """DTO for paginated product listing."""
    products: List[ProductResponseDTO]
    total: int
    page: int
    limit: int
