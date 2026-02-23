from fastapi import status
from loguru import logger

from app.schemas import CreateOrderSchema, OrderResponseSchema, OrderStatusEnum
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    OrderValidationError,
    AuthorizationError,
    PaymentError,
    EmailError,
    DatabaseError
)
from app.models import (
    create_order as model_create_order,
    find_order_by_id, get_orders_by_user,
    update_order_status as model_update_order_status,
)
from app.tasks import send_order_confirmation_email, process_payment


async def create_order(body: CreateOrderSchema, current_user: dict) -> OrderResponseSchema:
    # Validate order items
    if not body.items:
        raise OrderValidationError("Order must contain at least one item")
    
    # Validate each item
    for i, item in enumerate(body.items):
        if item.quantity <= 0:
            raise OrderValidationError(
                f"Item quantity must be greater than 0",
                item_index=i
            )
        if item.price <= 0:
            raise OrderValidationError(
                f"Item price must be greater than 0",
                item_index=i
            )
    
    # Validate shipping address
    if not body.shipping_address or not body.shipping_address.postal_code:
        raise OrderValidationError("Valid shipping address is required")
    
    # Validate payment method
    valid_payment_methods = ["stripe", "paypal", "cod"]
    if body.payment_method not in valid_payment_methods:
        raise OrderValidationError(
            f"Invalid payment method. Must be one of: {', '.join(valid_payment_methods)}"
        )
    
    total_amount = sum(item.price * item.quantity for item in body.items)
    
    # Minimum order amount validation
    if total_amount < 1:
        raise OrderValidationError("Order total must be at least $1.00")

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
    # Validate status transitions
    valid_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["processing", "cancelled"],
        "processing": ["shipped", "cancelled"],
        "shipped": ["delivered", "returned"],
        "delivered": ["returned"],
        "cancelled": [],
        "returned": []
    }
    
    try:
        order = find_order_by_id(order_id)
        if not order:
            raise NotFoundError("order", order_id)
        
        current_status = order.get("status")
        if new_status.value not in valid_transitions.get(current_status, []):
            raise OrderValidationError(
                f"Cannot transition from {current_status} to {new_status.value}"
            )
        
        updated_order = model_update_order_status(order_id, new_status)
        if not updated_order:
            raise DatabaseError("update_order_status", "Failed to update order status")
        
    except (NotFoundError, OrderValidationError, DatabaseError):
        raise
    except Exception as e:
        raise DatabaseError("update_order_status", str(e))

    logger.info("Order status updated | order_id={} status={}", order_id, new_status)
    return OrderResponseSchema(**updated_order)
