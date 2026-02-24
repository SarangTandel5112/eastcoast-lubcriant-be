from fastapi import APIRouter, status, Depends

from app.modules.order.order_dto import CreateOrderRequestDTO, OrderStatusEnum
from app.common.response import respond
from app.core import get_current_user, require_admin
from app.modules.order import order_controller

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order(
    body: CreateOrderRequestDTO,
    current_user: dict = Depends(get_current_user),
):
    order = await order_controller.create_order(body, current_user)
    return respond(data=order, message="Order placed successfully", status_code=201)


@router.get("/my-orders")
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    orders = await order_controller.get_my_orders(current_user)
    return respond(data=orders, message="Orders fetched")


@router.get("/{order_id}")
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = await order_controller.get_order(order_id, current_user)
    return respond(data=order, message="Order fetched")


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    new_status: OrderStatusEnum,
    admin: dict = Depends(require_admin),
):
    order = await order_controller.update_order_status(order_id, new_status)
    return respond(data=order, message="Order status updated")
