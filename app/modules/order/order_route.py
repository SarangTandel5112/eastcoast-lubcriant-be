from fastapi import APIRouter, status, Depends, Request

from app.modules.order.order_dto import CreateOrderRequestDTO, OrderStatusEnum
from app.common.response import respond
from app.core import get_current_user, require_admin
from app.core.rate_limit import limiter, RateLimits
from app.modules.order import order_service  # Import service directly

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.API_WRITE)
async def create_order(
    request: Request,
    body: CreateOrderRequestDTO,
    current_user: dict = Depends(get_current_user),
):
    """Create a new order for the current user."""
    order = await order_service.create_order(body, current_user)
    return respond(data=order, message="Order placed successfully", status_code=201)


@router.get("/my-orders")
@limiter.limit(RateLimits.API_READ)
async def get_my_orders(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get all orders for the current user."""
    orders = await order_service.get_my_orders(current_user)
    return respond(data=orders, message="Orders fetched")


@router.get("/{order_id}")
@limiter.limit(RateLimits.API_READ)
async def get_order(
    request: Request,
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific order by ID."""
    order = await order_service.get_order(order_id, current_user)
    return respond(data=order, message="Order fetched")


@router.patch("/{order_id}/status")
@limiter.limit(RateLimits.API_WRITE)
async def update_order_status(
    request: Request,
    order_id: str,
    new_status: OrderStatusEnum,
    admin: dict = Depends(require_admin),
):
    """Update order status (admin only)."""
    order = await order_service.update_order_status(order_id, new_status, admin)
    return respond(data=order, message="Order status updated")
