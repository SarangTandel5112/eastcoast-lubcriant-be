from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    OrderValidationError,
    NotFoundError,
    AuthorizationError,
    DatabaseError,
)
from app.modules.order.order_dto import (
    CreateOrderRequestDTO,
    OrderResponseDTO,
    OrderStatusEnum,
)
from app.modules.order.order_dco import OrderDCO, OrderItemDCO, ShippingAddressDCO
from app.modules.order.order_model import (
    create_order as model_create_order,
    find_order_by_id,
    get_orders_by_user,
    update_order_status as model_update_order_status,
)
from app.common.utils import sanitize_text


# Valid status transitions map
VALID_STATUS_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered", "returned"],
    "delivered": ["returned"],
    "cancelled": [],
    "returned": [],
}

VALID_PAYMENT_METHODS = ["stripe", "paypal", "cod"]


def validate_order_items(items) -> None:
    """Validate order items — check quantities and prices."""
    if not items:
        raise OrderValidationError("Order must contain at least one item")

    for i, item in enumerate(items):
        if item.quantity <= 0:
            raise OrderValidationError(
                "Item quantity must be greater than 0",
                item_index=i,
            )
        if item.price <= 0:
            raise OrderValidationError(
                "Item price must be greater than 0",
                item_index=i,
            )


def validate_shipping_address(shipping_address) -> None:
    """Validate shipping address has required fields."""
    if not shipping_address or not shipping_address.postal_code:
        raise OrderValidationError("Valid shipping address is required")


def validate_payment_method(payment_method: str) -> None:
    """Validate payment method is one of the accepted types."""
    if payment_method not in VALID_PAYMENT_METHODS:
        raise OrderValidationError(
            f"Invalid payment method. Must be one of: {', '.join(VALID_PAYMENT_METHODS)}"
        )


def validate_order_total(total_amount: float) -> None:
    """Validate minimum order amount."""
    if total_amount < 1:
        raise OrderValidationError("Order total must be at least $1.00")


def calculate_order_total(items) -> float:
    """Calculate total amount from order items."""
    return sum(item.price * item.quantity for item in items)


def validate_status_transition(current_status: str, new_status: str) -> None:
    """Validate that the status transition is allowed."""
    allowed = VALID_STATUS_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise OrderValidationError(
            f"Cannot transition from {current_status} to {new_status}"
        )


# ── Service Layer Functions (Business Logic) ────────────────


async def create_order(
    session: AsyncSession,
    body: CreateOrderRequestDTO,
    current_user: dict
) -> OrderResponseDTO:
    """Create a new order for the authenticated user."""
    validate_order_items(body.items)
    validate_shipping_address(body.shipping_address)
    validate_payment_method(body.payment_method)

    total_amount = calculate_order_total(body.items)
    validate_order_total(total_amount)

    sanitized_address = ShippingAddressDCO(
        full_name=sanitize_text(body.shipping_address.full_name),
        address_line1=sanitize_text(body.shipping_address.address_line1),
        address_line2=sanitize_text(body.shipping_address.address_line2) if body.shipping_address.address_line2 else None,
        city=sanitize_text(body.shipping_address.city),
        state=sanitize_text(body.shipping_address.state),
        postal_code=sanitize_text(body.shipping_address.postal_code),
        country=body.shipping_address.country,
    )

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
        shipping_address=sanitized_address,
        total_amount=total_amount,
    )

    try:
        created = await model_create_order(session, dco)
    except Exception as e:
        logger.error("Failed to create order | error={}", str(e))
        raise DatabaseError("create_order", str(e))

    # Fire background tasks (non-blocking, skipped if Celery unavailable)
    try:
        from app.modules.order.order_tasks import (
            send_order_confirmation_email,
            process_payment
        )
        process_payment.delay(created.id, total_amount, body.payment_method)
        send_order_confirmation_email.delay(current_user["user_id"], created.id)
    except Exception as e:
        logger.warning(
            "Celery not available, background tasks skipped | order_id={} error={}",
            created.id,
            str(e)
        )

    logger.info(
        "Order created | order_id={} user_id={} total=${:.2f}",
        created.id,
        current_user["user_id"],
        total_amount,
    )

    return OrderResponseDTO.from_dco(created)


async def get_my_orders(session: AsyncSession, current_user: dict) -> list[OrderResponseDTO]:
    """Get all orders for the current user."""
    orders = await get_orders_by_user(session, current_user["user_id"])
    return [OrderResponseDTO.from_dco(o) for o in orders]


async def get_order(session: AsyncSession, order_id: str, current_user: dict) -> OrderResponseDTO:
    """Get a specific order by ID."""
    order = await find_order_by_id(session, order_id)
    if not order:
        raise NotFoundError("order", order_id)

    # Authorization: Users can only see their own orders; admins can see all
    if current_user["role"] != "ADMIN" and order.user_id != current_user["user_id"]:
        raise AuthorizationError(
            "You can only view your own orders",
            required_role="ADMIN"
        )

    return OrderResponseDTO.from_dco(order)


async def update_order_status(
    session: AsyncSession,
    order_id: str,
    new_status: OrderStatusEnum,
    admin_user: dict
) -> OrderResponseDTO:
    """Update order status (admin only)."""
    try:
        order = await find_order_by_id(session, order_id)
        if not order:
            raise NotFoundError("order", order_id)

        validate_status_transition(order.status, new_status.value)

        updated_order = await model_update_order_status(session, order_id, new_status.value)
        if not updated_order:
            raise DatabaseError("update_order_status", "Failed to update order status")

    except (NotFoundError, OrderValidationError, DatabaseError):
        raise
    except Exception as e:
        logger.error("Failed to update order status | error={}", str(e))
        raise DatabaseError("update_order_status", str(e))

    logger.info(
        "Order status updated | order_id={} old_status={} new_status={} by admin={}",
        order_id,
        order.status,
        new_status.value,
        admin_user["user_id"]
    )

    return OrderResponseDTO.from_dco(updated_order)
