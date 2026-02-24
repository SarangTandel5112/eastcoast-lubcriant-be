from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.order.order_dto import CreateOrderRequestDTO, OrderResponseDTO, OrderStatusEnum
from app.modules.order.order_dco import OrderDCO, OrderItemDCO, ShippingAddressDCO
from app.core.exceptions import (
    NotFoundError,
    AuthorizationError,
    DatabaseError,
)
from app.modules.order.order_model import (
    create_order as model_create_order,
    find_order_by_id,
    get_orders_by_user,
    update_order_status as model_update_order_status,
)
from app.modules.order.order_service import (
    validate_order_items,
    validate_shipping_address,
    validate_payment_method,
    validate_order_total,
    calculate_order_total,
    validate_status_transition,
)


async def create_order(
    session: AsyncSession, body: CreateOrderRequestDTO, current_user: dict
) -> OrderResponseDTO:
    validate_order_items(body.items)
    validate_shipping_address(body.shipping_address)
    validate_payment_method(body.payment_method)

    total_amount = calculate_order_total(body.items)
    validate_order_total(total_amount)

    dco = OrderDCO(
        user_id=current_user["user_id"],
        items=[
            OrderItemDCO(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in body.items
        ],
        shipping_address=ShippingAddressDCO(
            full_name=body.shipping_address.full_name,
            address_line1=body.shipping_address.address_line1,
            address_line2=body.shipping_address.address_line2,
            city=body.shipping_address.city,
            state=body.shipping_address.state,
            postal_code=body.shipping_address.postal_code,
            country=body.shipping_address.country,
        ),
        total_amount=total_amount,
    )

    try:
        created = await model_create_order(session, dco)
    except Exception as e:
        raise DatabaseError("create_order", str(e))

    try:
        from app.modules.order.order_tasks import send_order_confirmation_email, process_payment
        process_payment.delay(created.id, total_amount, body.payment_method)
        send_order_confirmation_email.delay(current_user["user_id"], created.id)
    except Exception:
        logger.warning("Celery not available, background tasks skipped | order_id={}", created.id)

    logger.info(
        "Order created | order_id={} user_id={} total={}",
        created.id, current_user["user_id"], total_amount,
    )
    return OrderResponseDTO.from_dco(created)


async def get_my_orders(session: AsyncSession, current_user: dict) -> list[OrderResponseDTO]:
    orders = await get_orders_by_user(session, current_user["user_id"])
    return [OrderResponseDTO.from_dco(o) for o in orders]


async def get_order(
    session: AsyncSession, order_id: str, current_user: dict
) -> OrderResponseDTO:
    order = await find_order_by_id(session, order_id)
    if not order:
        raise NotFoundError("order", order_id)

    if current_user["role"] != "admin" and order.user_id != current_user["user_id"]:
        raise AuthorizationError(
            "Access denied",
            required_role="admin"
        )

    return OrderResponseDTO.from_dco(order)


async def update_order_status(
    session: AsyncSession, order_id: str, new_status: OrderStatusEnum
) -> OrderResponseDTO:
    try:
        order = await find_order_by_id(session, order_id)
        if not order:
            raise NotFoundError("order", order_id)

        validate_status_transition(order.status, new_status.value)

        updated_order = await model_update_order_status(session, order_id, new_status.value)
        if not updated_order:
            raise DatabaseError("update_order_status", "Failed to update order status")

    except (NotFoundError, DatabaseError):
        raise
    except Exception as e:
        raise DatabaseError("update_order_status", str(e))

    logger.info("Order status updated | order_id={} status={}", order_id, new_status)
    return OrderResponseDTO.from_dco(updated_order)
