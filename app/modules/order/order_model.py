"""Order model layer — async database operations for `orders` and `order_items` tables."""

from typing import Optional
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.order.order_dco import OrderDCO, OrderItemDCO, ShippingAddressDCO
from app.modules.order.order_entity import OrderEntity, OrderItemEntity


# ── Entity ↔ DCO helpers ─────────────────────────────────────

def _order_entity_to_dco(entity: OrderEntity) -> OrderDCO:
    """Convert an OrderEntity (with loaded items) to an OrderDCO."""
    return OrderDCO(
        id=str(entity.id),
        user_id=str(entity.user_id),
        items=[
            OrderItemDCO(
                product_id=str(item.product_id) if item.product_id else "",
                quantity=item.quantity,
                price=item.price,
            )
            for item in (entity.items or [])
        ],
        shipping_address=ShippingAddressDCO(
            full_name=entity.shipping_full_name,
            address_line1=entity.shipping_address_line1,
            address_line2=entity.shipping_address_line2,
            city=entity.shipping_city,
            state=entity.shipping_state,
            postal_code=entity.shipping_postal_code,
            country=entity.shipping_country,
        ),
        status=entity.status,
        total_amount=entity.total_amount,
        payment_intent_id=entity.payment_intent_id,
        created_at=entity.created_at.isoformat() if entity.created_at else "",
    )


def _dco_to_order_entity(dco: OrderDCO) -> OrderEntity:
    """Convert an OrderDCO to a new OrderEntity for INSERT (with nested items)."""
    try:
        user_uid = uuid.UUID(dco.user_id)
    except ValueError:
        user_uid = uuid.uuid4()

    entity = OrderEntity(
        user_id=user_uid,
        status=dco.status,
        total_amount=dco.total_amount,
        payment_intent_id=dco.payment_intent_id,
        shipping_full_name=dco.shipping_address.full_name,
        shipping_address_line1=dco.shipping_address.address_line1,
        shipping_address_line2=dco.shipping_address.address_line2,
        shipping_city=dco.shipping_address.city,
        shipping_state=dco.shipping_address.state,
        shipping_postal_code=dco.shipping_address.postal_code,
        shipping_country=dco.shipping_address.country,
        items=[],
    )

    for item_dco in dco.items:
        product_uid = None
        if item_dco.product_id:
            try:
                product_uid = uuid.UUID(item_dco.product_id)
            except ValueError:
                pass

        entity.items.append(
            OrderItemEntity(
                product_id=product_uid,
                quantity=item_dco.quantity,
                price=item_dco.price,
            )
        )

    return entity


# ── CRUD operations ──────────────────────────────────────────

async def create_order(session: AsyncSession, dco: OrderDCO) -> OrderDCO:
    """Insert a new order (with items) and return the hydrated DCO."""
    entity = _dco_to_order_entity(dco)
    session.add(entity)
    await session.flush()
    await session.refresh(entity)

    logger.debug("Order row inserted | id={}", entity.id)
    return _order_entity_to_dco(entity)


async def find_order_by_id(session: AsyncSession, order_id: str) -> Optional[OrderDCO]:
    """Lookup an order by UUID (items loaded eagerly via selectin). Returns None if not found."""
    try:
        oid = uuid.UUID(order_id)
    except ValueError:
        return None

    result = await session.execute(
        select(OrderEntity).where(OrderEntity.id == oid)
    )
    entity = result.scalar_one_or_none()
    return _order_entity_to_dco(entity) if entity else None


async def get_orders_by_user(session: AsyncSession, user_id: str) -> list[OrderDCO]:
    """Return all orders for a given user, newest first."""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return []

    result = await session.execute(
        select(OrderEntity)
        .where(OrderEntity.user_id == uid)
        .order_by(OrderEntity.created_at.desc())
    )
    entities = result.scalars().all()
    return [_order_entity_to_dco(e) for e in entities]


async def update_order_status(
    session: AsyncSession, order_id: str, new_status: str
) -> Optional[OrderDCO]:
    """Update an order's status. Returns the updated DCO or None if not found."""
    try:
        oid = uuid.UUID(order_id)
    except ValueError:
        return None

    result = await session.execute(
        select(OrderEntity).where(OrderEntity.id == oid)
    )
    entity = result.scalar_one_or_none()
    if not entity:
        return None

    entity.status = new_status
    await session.flush()
    await session.refresh(entity)
    return _order_entity_to_dco(entity)
