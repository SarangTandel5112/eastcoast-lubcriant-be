from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CategoryEnum(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    books = "books"
    other = "other"


class CreateProductSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: CategoryEnum
    images: List[str] = []
    tags: List[str] = []


class UpdateProductSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[CategoryEnum] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ProductResponseSchema(BaseModel):
    id: str
    name: str
    description: str
    price: float
    stock: int
    category: str
    images: List[str]
    tags: List[str]


class ProductListSchema(BaseModel):
    products: List[ProductResponseSchema]
    total: int
    page: int
    limit: int
