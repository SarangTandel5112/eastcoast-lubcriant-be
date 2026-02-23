from app.core.exceptions import OrderValidationError


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
