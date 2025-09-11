# backend/create_admin.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from backend.auth import hash_password
from backend.database import db

async def create_admin():
    username = input("Enter admin username: ").strip()
    password = input("Enter admin password: ").strip()

    password_hash = hash_password(password)

    existing = await db.admins.find_one({"username": username})
    if existing:
        print(f"⚠️ Admin '{username}' already exists! Updating password...")
        await db.admins.update_one(
            {"username": username},
            {"$set": {"password_hash": password_hash}}
        )
        print(f"✅ Password updated for admin '{username}'!")
    else:
        await db.admins.insert_one({
            "username": username,
            "password_hash": password_hash
        })
        print(f"✅ Admin '{username}' created successfully!")

if __name__ == "__main__":
    asyncio.run(create_admin())
