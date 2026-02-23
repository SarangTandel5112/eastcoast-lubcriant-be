from loguru import logger

from app.modules.order.order_schema import CreateOrderSchema, OrderResponseSchema, OrderStatusEnum
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
from app.modules.order.order_tasks import send_order_confirmation_email, process_payment


async def create_order(body: CreateOrderSchema, current_user: dict) -> OrderResponseSchema:
    # Validate order data
    validate_order_items(body.items)
    validate_shipping_address(body.shipping_address)
    validate_payment_method(body.payment_method)

    total_amount = calculate_order_total(body.items)
    validate_order_total(total_amount)

    try:
        order = model_create_order(
            user_id=current_user["user_id"],
            items=[item.model_dump() for item in body.items],
            shipping_address=body.shipping_address.model_dump(),
            total_amount=total_amount,
            payment_method=body.payment_method,
        )
    except Exception as e:
        raise DatabaseError("create_order", str(e))

    # ── Fire background tasks (non-blocking, skipped if Redis/Celery unavailable)
    try:
        process_payment.delay(order["id"], total_amount, body.payment_method)
        send_order_confirmation_email.delay(current_user["user_id"], order["id"])
    except Exception:
        logger.warning("Celery not available, background tasks skipped | order_id={}", order["id"])

    logger.info(
        "Order created | order_id={} user_id={} total={}",
        order["id"], current_user["user_id"], total_amount,
    )
    return OrderResponseSchema(**order)


async def get_my_orders(current_user: dict) -> list[OrderResponseSchema]:
    orders = get_orders_by_user(current_user["user_id"])
    return [OrderResponseSchema(**o) for o in orders]


async def get_order(order_id: str, current_user: dict) -> OrderResponseSchema:
    order = find_order_by_id(order_id)
    if not order:
        raise NotFoundError("order", order_id)

    # Users can only see their own orders; admins can see all
    if current_user["role"] != "admin" and order["user_id"] != current_user["user_id"]:
        raise AuthorizationError(
            "Access denied",
            required_role="admin"
        )

    return OrderResponseSchema(**order)


async def update_order_status(
    order_id: str, new_status: OrderStatusEnum
) -> OrderResponseSchema:
    try:
        order = find_order_by_id(order_id)
        if not order:
            raise NotFoundError("order", order_id)

        current_status = order.get("status")
        validate_status_transition(current_status, new_status.value)

        updated_order = model_update_order_status(order_id, new_status)
        if not updated_order:
            raise DatabaseError("update_order_status", "Failed to update order status")

    except (NotFoundError, DatabaseError):
        raise
    except Exception as e:
        raise DatabaseError("update_order_status", str(e))

    logger.info("Order status updated | order_id={} status={}", order_id, new_status)
    return OrderResponseSchema(**updated_order)
