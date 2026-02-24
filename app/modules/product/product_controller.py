from loguru import logger

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
    page: int, limit: int, category: str = None, search: str = None
) -> ProductListResponseDTO:
    products = get_all_products(category=category, search=search)
    return paginate_products(products, page, limit)


async def get_product(product_id: str) -> ProductResponseDTO:
    dco = find_product_by_id(product_id)
    if not dco:
        raise NotFoundError("product", product_id)
    return ProductResponseDTO.from_dco(dco)


async def create_product(body: CreateProductRequestDTO, admin_user: dict) -> ProductResponseDTO:
    validate_create_product(body)

    # DTO → DCO conversion
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

    created = model_create_product(dco)
    logger.info("Product created | product_id={} by admin={}", created.id, admin_user["user_id"])
    return ProductResponseDTO.from_dco(created)


async def update_product(
    product_id: str, body: UpdateProductRequestDTO, admin_user: dict
) -> ProductResponseDTO:
    validate_update_product(body)

    update_data = body.model_dump(exclude_none=True)
    # Convert category enum to string value if present
    if "category" in update_data and update_data["category"] is not None:
        update_data["category"] = update_data["category"].value

    updated = model_update_product(product_id, update_data)
    if not updated:
        raise NotFoundError("product", product_id)

    logger.info("Product updated | product_id={}", product_id)
    return ProductResponseDTO.from_dco(updated)


async def delete_product(product_id: str, admin_user: dict) -> None:
    if not model_delete_product(product_id):
        raise NotFoundError("product", product_id)
    logger.info("Product deleted | product_id={}", product_id)
