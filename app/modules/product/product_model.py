"""Product model layer — async database operations for the `products` table."""

from typing import Optional
import uuid

from loguru import logger
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.product_dco import ProductDCO
from app.modules.product.product_entity import ProductEntity


# ── Entity ↔ DCO helpers ─────────────────────────────────────

def _entity_to_dco(entity: ProductEntity) -> ProductDCO:
    """Convert a SQLAlchemy entity to a domain object."""
    return ProductDCO(
        id=str(entity.id),
        name=entity.name,
        description=entity.description,
        price=entity.price,
        stock=entity.stock,
        category=entity.category,
        images=entity.images or [],
        tags=entity.tags or [],
        created_by=str(entity.created_by) if entity.created_by else "",
        created_at=entity.created_at.isoformat() if entity.created_at else "",
    )


def _dco_to_entity(dco: ProductDCO) -> ProductEntity:
    """Convert a domain object to a new SQLAlchemy entity for INSERT."""
    created_by = None
    if dco.created_by:
        try:
            created_by = uuid.UUID(dco.created_by)
        except ValueError:
            pass

    return ProductEntity(
        name=dco.name,
        description=dco.description,
        price=dco.price,
        stock=dco.stock,
        category=dco.category,
        images=dco.images,
        tags=dco.tags,
        created_by=created_by,
    )


# ── CRUD operations ──────────────────────────────────────────

async def create_product(session: AsyncSession, dco: ProductDCO) -> ProductDCO:
    """Insert a new product row and return the hydrated DCO."""
    entity = _dco_to_entity(dco)
    session.add(entity)
    await session.flush()
    await session.refresh(entity)

    logger.debug("Product row inserted | id={}", entity.id)
    return _entity_to_dco(entity)


async def find_product_by_id(session: AsyncSession, product_id: str) -> Optional[ProductDCO]:
    """Lookup a product by UUID. Returns None if not found."""
    try:
        pid = uuid.UUID(product_id)
    except ValueError:
        return None

    result = await session.execute(
        select(ProductEntity).where(ProductEntity.id == pid)
    )
    entity = result.scalar_one_or_none()
    return _entity_to_dco(entity) if entity else None


async def get_all_products(
    session: AsyncSession,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> list[ProductDCO]:
    """Return all products, optionally filtered by category and/or search query."""
    stmt = select(ProductEntity)

    if category:
        stmt = stmt.where(ProductEntity.category == category)
    if search:
        stmt = stmt.where(ProductEntity.name.ilike(f"%{search}%"))

    stmt = stmt.order_by(ProductEntity.created_at.desc())
    result = await session.execute(stmt)
    entities = result.scalars().all()
    return [_entity_to_dco(e) for e in entities]


async def update_product(
    session: AsyncSession, product_id: str, update_data: dict
) -> Optional[ProductDCO]:
    """Update a product by UUID. Returns the updated DCO or None if not found."""
    try:
        pid = uuid.UUID(product_id)
    except ValueError:
        return None

    result = await session.execute(
        select(ProductEntity).where(ProductEntity.id == pid)
    )
    entity = result.scalar_one_or_none()
    if not entity:
        return None

    for key, value in update_data.items():
        if hasattr(entity, key):
            setattr(entity, key, value)

    await session.flush()
    await session.refresh(entity)
    return _entity_to_dco(entity)


async def delete_product(session: AsyncSession, product_id: str) -> bool:
    """Delete a product by UUID. Returns True if deleted, False if not found."""
    try:
        pid = uuid.UUID(product_id)
    except ValueError:
        return False

    result = await session.execute(
        sa_delete(ProductEntity).where(ProductEntity.id == pid)
    )
    return result.rowcount > 0
