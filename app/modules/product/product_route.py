from fastapi import APIRouter, status, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.product_dto import CreateProductRequestDTO, UpdateProductRequestDTO
from app.common.response import respond
from app.core import require_admin, get_db_session
from app.core.rate_limit import limiter, RateLimits
from app.modules.product import product_service

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
                    FastAPICache.get_backend()
                    return await cached_func(*args, **kwargs)
                except AssertionError:
                    return await func(*args, **kwargs)

            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            import functools
            functools.update_wrapper(wrapper, func)
            return wrapper
        except ImportError:
            return func
    return decorator


@router.get("/")
@limiter.limit(RateLimits.API_READ)
@optional_cache(expire=60)
async def get_products(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db_session),
):
    """Get paginated list of products with optional filtering."""
    result = await product_service.list_products(db, page, limit, category, search)
    return respond(
        data=result,
        message="Products fetched",
        meta={"total": result.total, "page": result.page, "limit": result.limit},
    )


@router.get("/{product_id}")
@limiter.limit(RateLimits.API_READ)
@optional_cache(expire=120)
async def get_product(
    request: Request,
    product_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a single product by ID."""
    product = await product_service.get_product(db, product_id)
    return respond(data=product, message="Product fetched")


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.API_WRITE)
async def create_product(
    request: Request,
    body: CreateProductRequestDTO,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new product (admin only)."""
    product = await product_service.create_product(db, body, admin)
    return respond(data=product, message="Product created successfully", status_code=201)


@router.patch("/{product_id}")
@limiter.limit(RateLimits.API_WRITE)
async def update_product(
    request: Request,
    product_id: str,
    body: UpdateProductRequestDTO,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Update an existing product (admin only)."""
    product = await product_service.update_product(db, product_id, body, admin)
    return respond(data=product, message="Product updated successfully")


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(RateLimits.API_DELETE)
async def delete_product(
    request: Request,
    product_id: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a product (admin only)."""
    await product_service.delete_product(db, product_id, admin)
