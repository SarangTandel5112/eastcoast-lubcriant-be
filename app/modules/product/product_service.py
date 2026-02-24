from app.core.exceptions import (
    NotFoundError,
    ProductValidationError,
)
from app.modules.product.product_dto import ProductResponseDTO, ProductListResponseDTO
from app.modules.product.product_dco import ProductDCO


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
