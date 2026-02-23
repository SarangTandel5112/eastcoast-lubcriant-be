import httpx
from loguru import logger
from typing import Optional


class HTTPClient:
    """
    Reusable async HTTP client wrapper.
    Use this to call third-party APIs (Stripe, shipping providers, etc.)
    """

    def __init__(self, base_url: str, headers: Optional[dict] = None):
        self.base_url = base_url
        self.default_headers = headers or {}

    async def get(self, path: str, params: dict = None) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params,
                headers=self.default_headers,
            )
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{path}",
                json=payload,
                headers=self.default_headers,
            )
            response.raise_for_status()
            return response.json()


# ── Example: Shipping provider client ────────────────────
class ShippingClient(HTTPClient):
    def __init__(self, api_key: str):
        super().__init__(
            base_url="https://api.yourshippingprovider.com",
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def get_shipping_rates(self, from_zip: str, to_zip: str, weight: float) -> dict:
        logger.info("Fetching shipping rates | from={} to={} weight={}", from_zip, to_zip, weight)
        return await self.get("/rates", params={"from": from_zip, "to": to_zip, "weight": weight})

    async def create_shipment(self, order_data: dict) -> dict:
        logger.info("Creating shipment | order_id={}", order_data.get("order_id"))
        return await self.post("/shipments", payload=order_data)
