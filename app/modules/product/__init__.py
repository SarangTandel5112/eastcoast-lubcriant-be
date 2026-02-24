"""Product module — CRUD operations for products with admin access control."""

from app.modules.product.product_dto import (
    CategoryEnum,
    CreateProductRequestDTO,
    UpdateProductRequestDTO,
    ProductResponseDTO,
    ProductListResponseDTO,
)
from app.modules.product.product_dco import ProductDCO
from app.modules.product.product_model import (
    create_product,
    find_product_by_id,
    get_all_products,
    update_product,
    delete_product,
)

__all__ = [
    "CategoryEnum",
    "CreateProductRequestDTO",
    "UpdateProductRequestDTO",
    "ProductResponseDTO",
    "ProductListResponseDTO",
    "ProductDCO",
    "create_product",
    "find_product_by_id",
    "get_all_products",
    "update_product",
    "delete_product",
]
