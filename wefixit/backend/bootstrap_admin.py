# backend/bootstrap_admin.py
import asyncio
from backend.auth import hash_password
from backend.database import db
from backend.config import settings

async def create_admin():
    existing = await db.admins.find_one({"username": settings.BOOTSTRAP_ADMIN_USERNAME})
    if existing:
        print("✅ Admin already exists:", existing["username"])
        return
    await db.admins.insert_one({
        "username": settings.BOOTSTRAP_ADMIN_USERNAME,
        "password_hash": hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD),
    })
    print("✅ Admin created:", settings.BOOTSTRAP_ADMIN_USERNAME)

if __name__ == "__main__":
    asyncio.run(create_admin())
