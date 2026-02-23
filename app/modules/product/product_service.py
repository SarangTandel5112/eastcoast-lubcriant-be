from app.core.exceptions import (
    NotFoundError,
    ProductValidationError,
)
from app.modules.product.product_schema import ProductResponseSchema, ProductListSchema
from app.modules.product.product_model import (
    create_product as model_create_product,
    find_product_by_id,
    get_all_products,
    update_product as model_update_product,
    delete_product as model_delete_product,
)


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


def paginate_products(products: list[dict], page: int, limit: int) -> ProductListSchema:
    """Paginate a list of product dicts into a ProductListSchema."""
    total = len(products)
    start = (page - 1) * limit
    paginated = products[start: start + limit]

    return ProductListSchema(
        products=[ProductResponseSchema(**p) for p in paginated],
        total=total,
        page=page,
        limit=limit,
    )
