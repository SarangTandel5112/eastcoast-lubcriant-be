from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.product_dto import (
    CreateProductRequestDTO, UpdateProductRequestDTO,
    ProductResponseDTO, ProductListResponseDTO,
)
from app.modules.product.product_dco import ProductDCO
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
    session: AsyncSession, page: int, limit: int, category: str = None, search: str = None
) -> ProductListResponseDTO:
    products = await get_all_products(session, category=category, search=search)
    return paginate_products(products, page, limit)


async def get_product(session: AsyncSession, product_id: str) -> ProductResponseDTO:
    dco = await find_product_by_id(session, product_id)
    if not dco:
        raise NotFoundError("product", product_id)
    return ProductResponseDTO.from_dco(dco)


async def create_product(
    session: AsyncSession, body: CreateProductRequestDTO, admin_user: dict
) -> ProductResponseDTO:
    validate_create_product(body)

    dco = ProductDCO(
        name=body.name,
        description=body.description,
        price=body.price,
        stock=body.stock,
        category=body.category.value,
        images=body.images,
        tags=body.tags,
        created_by=admin_user["user_id"],
    )

    created = await model_create_product(session, dco)
    logger.info("Product created | product_id={} by admin={}", created.id, admin_user["user_id"])
    return ProductResponseDTO.from_dco(created)


async def update_product(
    session: AsyncSession, product_id: str, body: UpdateProductRequestDTO, admin_user: dict
) -> ProductResponseDTO:
    validate_update_product(body)

    update_data = body.model_dump(exclude_none=True)
    if "category" in update_data and update_data["category"] is not None:
        update_data["category"] = update_data["category"].value

    updated = await model_update_product(session, product_id, update_data)
    if not updated:
        raise NotFoundError("product", product_id)

    logger.info("Product updated | product_id={}", product_id)
    return ProductResponseDTO.from_dco(updated)


async def delete_product(session: AsyncSession, product_id: str, admin_user: dict) -> None:
    if not await model_delete_product(session, product_id):
        raise NotFoundError("product", product_id)
    logger.info("Product deleted | product_id={}", product_id)
