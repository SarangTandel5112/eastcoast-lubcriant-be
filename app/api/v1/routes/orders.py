from fastapi import APIRouter, status, Depends

from app.schemas import CreateOrderSchema, OrderResponseSchema, OrderStatusEnum
from app.core import get_current_user, require_admin
from app.controllers import order_controller

router = APIRouter()


@router.post("/", response_model=OrderResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: CreateOrderSchema,
    current_user: dict = Depends(get_current_user),
):
    return await order_controller.create_order(body, current_user)


@router.get("/my-orders", response_model=list[OrderResponseSchema])
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    return await order_controller.get_my_orders(current_user)


@router.get("/{order_id}", response_model=OrderResponseSchema)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    return await order_controller.get_order(order_id, current_user)


@router.patch("/{order_id}/status", response_model=OrderResponseSchema)
async def update_order_status(
    order_id: str,
    new_status: OrderStatusEnum,
    admin: dict = Depends(require_admin),
):
    return await order_controller.update_order_status(order_id, new_status)
