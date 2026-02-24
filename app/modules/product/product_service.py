from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundError,
    ProductValidationError,
)
from app.modules.product.product_dto import (
    CreateProductRequestDTO,
    UpdateProductRequestDTO,
    ProductResponseDTO,
    ProductListResponseDTO,
)
from app.modules.product.product_dco import ProductDCO
from app.modules.product.product_model import (
    create_product as model_create_product,
    find_product_by_id,
    get_all_products,
    update_product as model_update_product,
    delete_product as model_delete_product,
)
from app.common.utils import sanitize_text, sanitize_html


def validate_create_product(body) -> None:
    """Validate product data for creation."""
    if body.price <= 0:
        raise ProductValidationError("price", str(body.price), "Price must be greater than 0")

    if body.stock < 0:
        raise ProductValidationError("stock", str(body.stock), "Stock cannot be negative")

    if not body.name or len(body.name.strip()) < 2:
        raise ProductValidationError("name", body.name or "", "Product name must be at least 2 characters")


def validate_update_product(body) -> None:
    """Validate product data for update."""
    if body.price is not None and body.price <= 0:
        raise ProductValidationError("price", str(body.price), "Price must be greater than 0")

    if body.stock is not None and body.stock < 0:
        raise ProductValidationError("stock", str(body.stock), "Stock cannot be negative")

    if body.name is not None and len(body.name.strip()) < 2:
        raise ProductValidationError("name", body.name, "Product name must be at least 2 characters")


def paginate_products(products: list[ProductDCO], page: int, limit: int) -> ProductListResponseDTO:
    """Paginate a list of product DCOs into a ProductListResponseDTO."""
    total = len(products)
    start = (page - 1) * limit
    paginated = products[start: start + limit]

    return ProductListResponseDTO(
        products=[ProductResponseDTO.from_dco(p) for p in paginated],
        total=total,
        page=page,
        limit=limit,
    )


# ── Service Layer Functions (Business Logic) ────────────────


async def list_products(
    session: AsyncSession, page: int, limit: int, category: str = None, search: str = None
) -> ProductListResponseDTO:
    """Get paginated list of products with optional filtering."""
    products = await get_all_products(session, category=category, search=search)
    return paginate_products(products, page, limit)


async def get_product(session: AsyncSession, product_id: str) -> ProductResponseDTO:
    """Get a single product by ID."""
    dco = await find_product_by_id(session, product_id)
    if not dco:
        raise NotFoundError("product", product_id)
    return ProductResponseDTO.from_dco(dco)


async def create_product(
    session: AsyncSession,
    body: CreateProductRequestDTO,
    admin_user: dict
) -> ProductResponseDTO:
    """Create a new product (admin only)."""
    validate_create_product(body)

    sanitized_name = sanitize_text(body.name)
    sanitized_description = sanitize_html(body.description)

    dco = ProductDCO(
        name=sanitized_name,
        description=sanitized_description,
        price=body.price,
        stock=body.stock,
        category=body.category.value,
        images=body.images,
        tags=[sanitize_text(tag) for tag in body.tags],
        created_by=admin_user["user_id"],
    )

    created = await model_create_product(session, dco)

    logger.info(
        "Product created | product_id={} by admin={}",
        created.id,
        admin_user["user_id"]
    )

    return ProductResponseDTO.from_dco(created)


async def update_product(
    session: AsyncSession,
    product_id: str,
    body: UpdateProductRequestDTO,
    admin_user: dict
) -> ProductResponseDTO:
    """Update an existing product (admin only)."""
    validate_update_product(body)

    update_data = body.model_dump(exclude_none=True)

    if "name" in update_data:
        update_data["name"] = sanitize_text(update_data["name"])

    if "description" in update_data:
        update_data["description"] = sanitize_html(update_data["description"])

    if "tags" in update_data:
        update_data["tags"] = [sanitize_text(tag) for tag in update_data["tags"]]

    if "category" in update_data and update_data["category"] is not None:
        update_data["category"] = update_data["category"].value

    updated = await model_update_product(session, product_id, update_data)
    if not updated:
        raise NotFoundError("product", product_id)

    logger.info(
        "Product updated | product_id={} by admin={}",
        product_id,
        admin_user["user_id"]
    )

    return ProductResponseDTO.from_dco(updated)


async def delete_product(session: AsyncSession, product_id: str, admin_user: dict) -> None:
    """Delete a product (admin only)."""
    if not await model_delete_product(session, product_id):
        raise NotFoundError("product", product_id)

    logger.info(
        "Product deleted | product_id={} by admin={}",
        product_id,
        admin_user["user_id"]
    )
