"""Comprehensive endpoint verification and report generator."""

import asyncio
import json
import uuid
import httpx
import os
import asyncpg
from loguru import logger
from tabulate import tabulate
from dotenv import load_dotenv

BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/api/v1"

class EndpointTester:
    def __init__(self):
        self.results = []
        self.client = httpx.AsyncClient(timeout=10.0)
        self.tokens = {}
        self.admin_tokens = {}
        self.created_ids = []

    async def promote_user(self, email: str):
        load_dotenv()
        dsn = os.getenv("DATABASE_URL")
        # Ensure asyncpg-ready DSN
        if "+asyncpg" in dsn:
            dsn = dsn.replace("+asyncpg", "")
        conn = await asyncpg.connect(dsn)
        try:
            await conn.execute("UPDATE users SET role = 'ADMIN' WHERE email = $1", email)
            logger.info(f"Promoted {email} to ADMIN")
        finally:
            await conn.close()

    def log_result(self, method, endpoint, status, expected, comment=""):
        res = "✅ WORKING" if status == expected else "❌ FAILED"
        self.results.append([method, endpoint, status, expected, res, comment])

    async def run_tests(self):
        logger.info("Starting Comprehensive Endpoint Verification...")

        # 1. Health Check
        try:
            resp = await self.client.get(f"{BASE_URL}/health")
            self.log_result("GET", "/health", resp.status_code, 200)
        except Exception as e:
            self.log_result("GET", "/health", "ERROR", 200, str(e))

        # 2. Register Dealer
        uid = uuid.uuid4().hex[:6]
        dealer_payload = {
            "email": f"dealer_{uid}@test.com",
            "password": "Password123!@#",
            "businessName": f"Dealer Corp {uid}",
            "province": "Ontario",
            "contactName": "John Tester",
            "phone": f"+1 555 {str(uuid.uuid4().int)[:7]}"
        }
        resp = await self.client.post(f"{API_V1}/auth/register", json=dealer_payload)
        self.log_result("POST", "/auth/register", resp.status_code, 201)
        if resp.status_code == 201:
            self.created_ids.append(resp.json()["data"]["id"])

        # 3. Login Dealer
        resp = await self.client.post(f"{API_V1}/auth/login", json={
            "identifier": dealer_payload["email"],
            "password": dealer_payload["password"]
        })
        self.log_result("POST", "/auth/login", resp.status_code, 200)
        if resp.status_code == 200:
            self.tokens = resp.json()["data"]

        # 4. Auth Me (Protected)
        headers = {"Authorization": f"Bearer {self.tokens.get('accessToken')}"}
        resp = await self.client.get(f"{API_V1}/auth/me", headers=headers)
        self.log_result("GET", "/auth/me", resp.status_code, 200)

        # 5. Update Profile
        resp = await self.client.patch(f"{API_V1}/auth/me", headers=headers, json={"contactName": "Updated Name"})
        self.log_result("PATCH", "/auth/me", resp.status_code, 200)

        # 6. Token Refresh
        resp = await self.client.post(f"{API_V1}/auth/refresh", json={"refreshToken": self.tokens.get("refreshToken")})
        self.log_result("POST", "/auth/refresh", resp.status_code, 200)
        if resp.status_code == 200:
            self.tokens = resp.json()["data"]
            headers = {"Authorization": f"Bearer {self.tokens.get('accessToken')}"}

        # 7. Admin Register
        admin_uid = uuid.uuid4().hex[:6]
        admin_payload = {
            "email": f"admin_{admin_uid}@test.com",
            "password": "Password123!@#",
            "businessName": "Admin Office",
            "province": "Quebec",
            "contactName": "Master Admin",
            "phone": f"+1 555 {str(uuid.uuid4().int)[:7]}"
        }
        await self.client.post(f"{API_V1}/auth/register", json=admin_payload)
        await self.promote_user(admin_payload["email"])
        
        # Admin Login
        resp = await self.client.post(f"{API_V1}/auth/login", json={
            "identifier": admin_payload["email"],
            "password": admin_payload["password"]
        })
        if resp.status_code == 200:
            self.admin_tokens = resp.json()["data"]
            admin_headers = {"Authorization": f"Bearer {self.admin_tokens.get('accessToken')}"}

            # 8. List Users (Admin)
            resp = await self.client.get(f"{API_V1}/auth/users", headers=admin_headers)
            self.log_result("GET", "/auth/users", resp.status_code, 200)

            # 9. Create User (Admin)
            new_uid = uuid.uuid4().hex[:6]
            resp = await self.client.post(f"{API_V1}/auth/users", headers=admin_headers, json={
                "email": f"created_{new_uid}@test.com",
                "password": "Password123!@#",
                "businessName": "Created by Admin",
                "province": "Ontario",
                "phone": f"+1 555 {str(uuid.uuid4().int)[:7]}",
                "role": "DEALER"
            })
            self.log_result("POST", "/auth/users", resp.status_code, 201)
            created_user_id = resp.json()["data"]["id"] if resp.status_code == 201 else None

            # 10. Get User By ID
            if created_user_id:
                resp = await self.client.get(f"{API_V1}/auth/users/{created_user_id}", headers=admin_headers)
                self.log_result("GET", "/auth/users/{id}", resp.status_code, 200)

                # 11. Patch User
                resp = await self.client.patch(f"{API_V1}/auth/users/{created_user_id}", headers=admin_headers, json={"province": "Updated Prov"})
                self.log_result("PATCH", "/auth/users/{id}", resp.status_code, 200)

                # 12. Delete User
                resp = await self.client.delete(f"{API_V1}/auth/users/{created_user_id}", headers=admin_headers)
                self.log_result("DELETE", "/auth/users/{id}", resp.status_code, 204)

        # 13. Logout
        resp = await self.client.post(f"{API_V1}/auth/logout", headers=headers)
        self.log_result("POST", "/auth/logout", resp.status_code, 200)

        # Print Table
        print("\n### ENDPOINT VERIFICATION STATUS TABLE ###")
        print(tabulate(self.results, headers=["METHOD", "ENDPOINT", "STATUS", "EXPECTED", "RESULT", "COMMENT"], tablefmt="github"))
        print("\nGenerated at: 2026-03-01 01:40:00")

    async def close(self):
        await self.client.aclose()

if __name__ == "__main__":
    tester = EndpointTester()
    try:
        asyncio.run(tester.run_tests())
    finally:
        asyncio.run(tester.close())
