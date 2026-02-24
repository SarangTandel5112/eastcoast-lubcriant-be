from fastapi import APIRouter

# ── Auth (existing) ────────────────────────────────────────
from app.modules.auth.auth_route import router as auth_router

# ── Users & Addresses ─────────────────────────────────────
from app.modules.users.users_route import router as users_router
from app.modules.dealer_addresses.dealer_addresses_route import router as dealer_addresses_router

# ── Product Core ──────────────────────────────────────────
from app.modules.brands.brands_route import router as brands_router
from app.modules.product_types.product_types_route import router as product_types_router
from app.modules.categories.categories_route import router as categories_router
from app.modules.products.products_route import router as products_router

# ── Variants ──────────────────────────────────────────────
from app.modules.product_variants.product_variants_route import router as product_variants_router

# ── Media ─────────────────────────────────────────────────
from app.modules.product_images.product_images_route import router as product_images_router
from app.modules.variant_images.variant_images_route import router as variant_images_router

# ── Standards ─────────────────────────────────────────────
from app.modules.standards.standards_route import router as standards_router
from app.modules.product_variant_standards.product_variant_standards_route import router as pvs_router

# ── Attributes ────────────────────────────────────────────
from app.modules.attributes.attributes_route import router as attributes_router
from app.modules.product_variant_attributes.product_variant_attributes_route import router as pva_router

# ── Applications ──────────────────────────────────────────
from app.modules.applications.applications_route import router as applications_router
from app.modules.product_applications.product_applications_route import router as pa_router

# ── Warehouse & Inventory ─────────────────────────────────
from app.modules.warehouses.warehouses_route import router as warehouses_router
from app.modules.inventory.inventory_route import router as inventory_router
from app.modules.inventory_movements.inventory_movements_route import router as inv_movements_router

# ── Orders ────────────────────────────────────────────────
from app.modules.orders.orders_route import router as orders_router
from app.modules.order_items.order_items_route import router as order_items_router

# ── Payments ──────────────────────────────────────────────
from app.modules.payments.payments_route import router as payments_router

# ── Tax & Invoices ────────────────────────────────────────
from app.modules.tax_rules.tax_rules_route import router as tax_rules_router
from app.modules.invoices.invoices_route import router as invoices_router

# ── AI ────────────────────────────────────────────────────
from app.modules.ai_calls.ai_calls_route import router as ai_calls_router


router = APIRouter(prefix="/api/v1")

# Auth
router.include_router(auth_router,         prefix="/auth",                      tags=["Auth"])

# Users & Addresses
router.include_router(users_router,         prefix="/users",                     tags=["Users"])
router.include_router(dealer_addresses_router, prefix="/dealer-addresses",       tags=["Dealer Addresses"])

# Product Core
router.include_router(brands_router,        prefix="/brands",                    tags=["Brands"])
router.include_router(product_types_router, prefix="/product-types",             tags=["Product Types"])
router.include_router(categories_router,    prefix="/categories",                tags=["Categories"])
router.include_router(products_router,      prefix="/products",                  tags=["Products"])

# Variants
router.include_router(product_variants_router,  prefix="/product-variants",      tags=["Product Variants"])

# Media
router.include_router(product_images_router,    prefix="/product-images",        tags=["Product Images"])
router.include_router(variant_images_router,    prefix="/variant-images",        tags=["Variant Images"])

# Standards
router.include_router(standards_router,     prefix="/standards",                 tags=["Standards"])
router.include_router(pvs_router,           prefix="/product-variant-standards", tags=["Product Variant Standards"])

# Attributes
router.include_router(attributes_router,    prefix="/attributes",                tags=["Attributes"])
router.include_router(pva_router,           prefix="/product-variant-attributes", tags=["Product Variant Attributes"])

# Applications
router.include_router(applications_router,  prefix="/applications",              tags=["Applications"])
router.include_router(pa_router,            prefix="/product-applications",      tags=["Product Applications"])

# Warehouse & Inventory
router.include_router(warehouses_router,    prefix="/warehouses",                tags=["Warehouses"])
router.include_router(inventory_router,     prefix="/inventory",                 tags=["Inventory"])
router.include_router(inv_movements_router, prefix="/inventory-movements",       tags=["Inventory Movements"])

# Orders
router.include_router(orders_router,        prefix="/orders",                    tags=["Orders"])
router.include_router(order_items_router,   prefix="/order-items",               tags=["Order Items"])

# Payments
router.include_router(payments_router,      prefix="/payments",                  tags=["Payments"])

# Tax & Invoices
router.include_router(tax_rules_router,     prefix="/tax-rules",                 tags=["Tax Rules"])
router.include_router(invoices_router,      prefix="/invoices",                  tags=["Invoices"])

# AI
router.include_router(ai_calls_router,      prefix="/ai-calls",                  tags=["AI Calls"])
