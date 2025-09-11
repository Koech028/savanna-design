import asyncio
from passlib.context import CryptContext
from backend.database import db  # import your Mongo connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password():
    username = input("Enter admin username: ").strip()
    password = input("Enter new password: ").strip()
    password_hash = pwd_context.hash(password)

    result = await db.admins.update_one(
        {"username": username},
        {"$set": {"password_hash": password_hash}}
    )

    if result.modified_count > 0:
        print(f"✅ Password reset for '{username}'!")
    else:
        print(f"⚠️ No user found with username '{username}'.")

if __name__ == "__main__":
    asyncio.run(reset_password())
