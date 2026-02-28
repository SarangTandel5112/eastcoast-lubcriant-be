"""Comprehensive E2E Authentication & User Management Test Suite."""

import asyncio
import json
import uuid
import httpx
import os
import asyncpg
from loguru import logger
from dotenv import load_dotenv

BASE_URL = "http://localhost:8001/api/v1"

def gen_user_data(role="DEALER"):
    uid = uuid.uuid4().hex[:6]
    return {
        "email": f"test_{uid}@example.com",
        "password": "Password123!@#",
        "businessName": f"Test Business {uid}",
        "province": "Ontario",
        "contactName": f"User {uid}",
        "phone": f"+1 (555) {str(uuid.uuid4().int)[:7]}"
    }

async def promote_user_to_admin(email: str):
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    dsn = os.getenv("DATABASE_URL")
    if "+asyncpg" in dsn:
        dsn = dsn.replace("+asyncpg", "")
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute("UPDATE users SET role = 'ADMIN' WHERE email = $1", email)
        logger.info(f"User {email} promoted to ADMIN via asyncpg")
    finally:
        await conn.close()

async def test_auth_flow():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. ──── REGISTER DEALER ────
        logger.info("Test: Public Registration (Dealer)")
        dealer_data = gen_user_data()
        resp = await client.post(f"{BASE_URL}/auth/register", json=dealer_data)
        assert resp.status_code == 201, f"Reg failed: {resp.text}"
        dealer_id = resp.json()["data"]["id"]
        logger.success(f"Dealer registered: {dealer_id}")

        # 2. ──── LOGIN DEALER ────
        logger.info("Test: Login")
        login_resp = await client.post(f"{BASE_URL}/auth/login", json={
            "identifier": dealer_data["email"],
            "password": dealer_data["password"]
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        tokens = login_resp.json()["data"]
        access_token = tokens["accessToken"]
        refresh_token = tokens["refreshToken"]
        headers = {"Authorization": f"Bearer {access_token}"}
        logger.success("Login success")

        # 3. ──── GET PROFILE ────
        logger.info("Test: Get Profile (/me)")
        me_resp = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["data"]["email"] == dealer_data["email"]
        logger.success("Profile fetched correctly")

        # 4. ──── UPDATE PROFILE ────
        logger.info("Test: Update Profile")
        update_data = {"contactName": "Updated Name", "province": "Quebec"}
        upd_resp = await client.patch(f"{BASE_URL}/auth/me", headers=headers, json=update_data)
        assert upd_resp.status_code == 200
        assert upd_resp.json()["data"]["contactName"] == "Updated Name"
        logger.success("Profile updated")

        # 5. ──── TOKEN REFRESH ────
        logger.info("Test: Token Refresh")
        ref_resp = await client.post(f"{BASE_URL}/auth/refresh", json={"refreshToken": refresh_token})
        assert ref_resp.status_code == 200
        new_access_token = ref_resp.json()["data"]["accessToken"]
        headers = {"Authorization": f"Bearer {new_access_token}"}
        logger.success("Token refreshed")

        # 6. ──── LOGOUT ────
        logger.info("Test: Logout")
        out_resp = await client.post(f"{BASE_URL}/auth/logout", headers=headers)
        assert out_resp.status_code == 200
        logger.success("Logout successful")

        # 7. ──── VERIFY TOKEN REVOKED ────
        logger.info("Test: Token Revocation Check")
        me_resp = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        assert me_resp.status_code == 401, "Token should be revoked!"
        logger.success("Revocation verified")

        # 8. ──── ADMIN FLOW ────
        logger.info("Test: Admin Management Flow")
        admin_payload = gen_user_data(role="ADMIN")
        await client.post(f"{BASE_URL}/auth/register", json=admin_payload)
        
        await promote_user_to_admin(admin_payload["email"])

        # Login as Admin
        adm_login_resp = await client.post(f"{BASE_URL}/auth/login", json={
            "identifier": admin_payload["email"],
            "password": admin_payload["password"]
        })
        assert adm_login_resp.status_code == 200, "Admin login failed"
        adm_token = adm_login_resp.json()["data"]["accessToken"]
        adm_headers = {"Authorization": f"Bearer {adm_token}"}

        # Admin: List Users
        list_resp = await client.get(f"{BASE_URL}/auth/users", headers=adm_headers)
        assert list_resp.status_code == 200
        logger.success(f"Admin list users: {len(list_resp.json()['data'])} found")

        # Admin: Create User
        new_dealer_by_admin = gen_user_data()
        adm_create_resp = await client.post(f"{BASE_URL}/auth/users", headers=adm_headers, json=new_dealer_by_admin)
        assert adm_create_resp.status_code == 201
        new_uid = adm_create_resp.json()["data"]["id"]
        logger.success(f"Admin created user: {new_uid}")

        # Admin: Soft Delete
        del_resp = await client.delete(f"{BASE_URL}/auth/users/{new_uid}", headers=adm_headers)
        assert del_resp.status_code == 204, f"Delete failed: {del_resp.status_code} {del_resp.text}"
        logger.success("Admin soft-deleted user")

        # Admin: Verify Deleted (should be 404 or excluded from list)
        get_deleted = await client.get(f"{BASE_URL}/auth/users/{new_uid}", headers=adm_headers)
        assert get_deleted.status_code == 404, f"Should be 404 but got {get_deleted.status_code}"
        logger.success("Soft-delete verification complete")

        logger.info("─── ALL ENDPOINTS PERFECTLY VERIFIED ───")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
