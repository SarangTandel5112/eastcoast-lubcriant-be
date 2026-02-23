from fastapi import status
from loguru import logger

from app.schemas import (
    CreateProductSchema, UpdateProductSchema,
    ProductResponseSchema, ProductListSchema,
)
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ProductValidationError,
    AuthorizationError
)
from app.models import (
    create_product as model_create_product,
    find_product_by_id, get_all_products,
    update_product as model_update_product,
    delete_product as model_delete_product,
)


async def list_products(
    page: int, limit: int, category: str = None, search: str = None
) -> ProductListSchema:
    products = get_all_products(category=category, search=search)
    total = len(products)
    start = (page - 1) * limit
    paginated = products[start: start + limit]

    return ProductListSchema(
        products=[ProductResponseSchema(**p) for p in paginated],
        total=total,
        page=page,
        limit=limit,
    )


async def get_product(product_id: str) -> ProductResponseSchema:
    product = find_product_by_id(product_id)
    if not product:
        raise NotFoundError("product", product_id)
    return ProductResponseSchema(**product)


async def create_product(body: CreateProductSchema, admin_user: dict) -> ProductResponseSchema:
    # Validate product data
    if body.price <= 0:
        raise ProductValidationError("price", str(body.price), "Price must be greater than 0")
    
    if body.stock < 0:
        raise ProductValidationError("stock", str(body.stock), "Stock cannot be negative")
    
    if not body.name or len(body.name.strip()) < 2:
        raise ProductValidationError("name", body.name or "", "Product name must be at least 2 characters")
    
    product = model_create_product(data=body.model_dump(), admin_id=admin_user["user_id"])
    logger.info("Product created | product_id={} by admin={}", product["id"], admin_user["user_id"])
    return ProductResponseSchema(**product)


async def update_product(
    product_id: str, body: UpdateProductSchema, admin_user: dict
) -> ProductResponseSchema:
    # Validate update data
    if body.price is not None and body.price <= 0:
        raise ProductValidationError("price", str(body.price), "Price must be greater than 0")
    
    if body.stock is not None and body.stock < 0:
        raise ProductValidationError("stock", str(body.stock), "Stock cannot be negative")
    
    if body.name is not None and len(body.name.strip()) < 2:
        raise ProductValidationError("name", body.name, "Product name must be at least 2 characters")
    
    updated = model_update_product(product_id, body.model_dump(exclude_none=True))
    if not updated:
        raise NotFoundError("product", product_id)

    logger.info("Product updated | product_id={}", product_id)
    return ProductResponseSchema(**updated)


async def delete_product(product_id: str, admin_user: dict) -> None:
    if not model_delete_product(product_id):
        raise NotFoundError("product", product_id)
    logger.info("Product deleted | product_id={}", product_id)
