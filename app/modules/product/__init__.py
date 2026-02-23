"""Product module — CRUD operations for products with admin access control."""

from app.modules.product.product_schema import (
    CategoryEnum,
    CreateProductSchema,
    UpdateProductSchema,
    ProductResponseSchema,
    ProductListSchema,
)
from app.modules.product.product_model import (
    create_product,
    find_product_by_id,
    get_all_products,
    update_product,
    delete_product,
)

__all__ = [
    "CategoryEnum",
    "CreateProductSchema",
    "UpdateProductSchema",
    "ProductResponseSchema",
    "ProductListSchema",
    "create_product",
    "find_product_by_id",
    "get_all_products",
    "update_product",
    "delete_product",
]
