from loguru import logger

from app.modules.product.product_schema import (
    CreateProductSchema, UpdateProductSchema,
    ProductResponseSchema, ProductListSchema,
)
from app.core.exceptions import NotFoundError
from app.modules.product.product_model import (
    create_product as model_create_product,
    find_product_by_id,
    get_all_products,
    update_product as model_update_product,
    delete_product as model_delete_product,
)
from app.modules.product.product_service import (
    validate_create_product,
    validate_update_product,
    paginate_products,
)


async def list_products(
    page: int, limit: int, category: str = None, search: str = None
) -> ProductListSchema:
    products = get_all_products(category=category, search=search)
    return paginate_products(products, page, limit)


async def get_product(product_id: str) -> ProductResponseSchema:
    product = find_product_by_id(product_id)
    if not product:
        raise NotFoundError("product", product_id)
    return ProductResponseSchema(**product)


async def create_product(body: CreateProductSchema, admin_user: dict) -> ProductResponseSchema:
    validate_create_product(body)
    
    product = model_create_product(data=body.model_dump(), admin_id=admin_user["user_id"])
    logger.info("Product created | product_id={} by admin={}", product["id"], admin_user["user_id"])
    return ProductResponseSchema(**product)


async def update_product(
    product_id: str, body: UpdateProductSchema, admin_user: dict
) -> ProductResponseSchema:
    validate_update_product(body)
    
    updated = model_update_product(product_id, body.model_dump(exclude_none=True))
    if not updated:
        raise NotFoundError("product", product_id)

    logger.info("Product updated | product_id={}", product_id)
    return ProductResponseSchema(**updated)


async def delete_product(product_id: str, admin_user: dict) -> None:
    if not model_delete_product(product_id):
        raise NotFoundError("product", product_id)
    logger.info("Product deleted | product_id={}", product_id)
