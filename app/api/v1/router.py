from fastapi import APIRouter
from app.api.v1.routes import auth, products, orders

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(orders.router,   prefix="/orders",   tags=["Orders"])

# ── Add new routers here ─────────────────────────────────
# router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
