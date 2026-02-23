from fastapi import APIRouter
from app.modules.auth.auth_route import router as auth_router
from app.modules.product.product_route import router as product_router
from app.modules.order.order_route import router as order_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router,    prefix="/auth",     tags=["Auth"])
router.include_router(product_router, prefix="/products", tags=["Products"])
router.include_router(order_router,   prefix="/orders",   tags=["Orders"])

# ── Add new module routers here ──────────────────────────
# from app.modules.reviews.review_route import router as review_router
# router.include_router(review_router, prefix="/reviews", tags=["Reviews"])
