from fastapi import APIRouter, status, Depends, Query

from app.modules.product.product_dto import CreateProductRequestDTO, UpdateProductRequestDTO
from app.common.response import respond
from app.core import require_admin
from app.modules.product import product_controller

router = APIRouter()


# ── Optional caching decorator ────────────────────────────
def optional_cache(expire: int):
    """Apply @cache only if FastAPICache is initialized, otherwise no-op.
    The check happens at request time, not import time."""
    def decorator(func):
        try:
            from fastapi_cache.decorator import cache as _cache
            from fastapi_cache import FastAPICache

            cached_func = _cache(expire=expire)(func)

            async def wrapper(*args, **kwargs):
                try:
                    # Check if FastAPICache backend is initialized
                    FastAPICache.get_backend()
                    return await cached_func(*args, **kwargs)
                except AssertionError:
                    # Cache not initialized, skip caching
                    return await func(*args, **kwargs)

            # Preserve function metadata for FastAPI
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            import functools
            functools.update_wrapper(wrapper, func)
            return wrapper
        except ImportError:
            return func
    return decorator


@router.get("/")
@optional_cache(expire=60)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    search: str = Query(None),
):
    result = await product_controller.list_products(page, limit, category, search)
    return respond(
        data=result,
        message="Products fetched",
        meta={"total": result.total, "page": result.page, "limit": result.limit},
    )


@router.get("/{product_id}")
@optional_cache(expire=120)
async def get_product(product_id: str):
    product = await product_controller.get_product(product_id)
    return respond(data=product, message="Product fetched")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    body: CreateProductRequestDTO,
    admin: dict = Depends(require_admin),
):
    product = await product_controller.create_product(body, admin)
    return respond(data=product, message="Product created successfully", status_code=201)


@router.patch("/{product_id}")
async def update_product(
    product_id: str,
    body: UpdateProductRequestDTO,
    admin: dict = Depends(require_admin),
):
    product = await product_controller.update_product(product_id, body, admin)
    return respond(data=product, message="Product updated successfully")


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    admin: dict = Depends(require_admin),
):
    await product_controller.delete_product(product_id, admin)
