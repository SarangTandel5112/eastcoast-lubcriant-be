import asyncio
import asyncpg
import os

async def test_conn():
    dsns = [
        "postgresql://postgres:postgres_password@127.0.0.1:5432/ecommerce_local",
        "postgresql://postgres:postgres_password@localhost:5432/ecommerce_local",
        "postgresql://postgres:postgres_password@172.18.0.3:5432/ecommerce_local"
    ]
    for dsn in dsns:
        print(f"Testing {dsn}...")
        try:
            conn = await asyncpg.connect(dsn)
            print(f"✅ Success: {dsn}")
            await conn.close()
        except Exception as e:
            print(f"❌ Failed: {dsn} | error={e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
