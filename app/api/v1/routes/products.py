from fastapi import APIRouter, status, Depends, Query

from app.schemas import CreateProductSchema, UpdateProductSchema, ProductResponseSchema, ProductListSchema
from app.core import require_admin
from app.controllers import product_controller

router = APIRouter()

# ── Optional caching decorator ────────────────────────────
try:
    from fastapi_cache.decorator import cache as _cache
    from fastapi_cache import FastAPICache
    # Test if cache backend is initialized
    _cache_available = True
except Exception:
    _cache_available = False


def optional_cache(expire: int):
    """Apply @cache only if Redis is available, otherwise no-op."""
    if _cache_available:
        try:
            return _cache(expire=expire)
        except Exception:
            pass
    # Return a no-op decorator
    return lambda func: func


@router.get("/", response_model=ProductListSchema)
@optional_cache(expire=60)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    search: str = Query(None),
):
    return await product_controller.list_products(page, limit, category, search)


@router.get("/{product_id}", response_model=ProductResponseSchema)
@optional_cache(expire=120)
async def get_product(product_id: str):
    return await product_controller.get_product(product_id)


@router.post("/", response_model=ProductResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    body: CreateProductSchema,
    admin: dict = Depends(require_admin),
):
    return await product_controller.create_product(body, admin)


@router.patch("/{product_id}", response_model=ProductResponseSchema)
async def update_product(
    product_id: str,
    body: UpdateProductSchema,
    admin: dict = Depends(require_admin),
):
    return await product_controller.update_product(product_id, body, admin)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    admin: dict = Depends(require_admin),
):
    await product_controller.delete_product(product_id, admin)
