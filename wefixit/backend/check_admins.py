# check_admins.py
import asyncio
from backend.database import db

async def main():
    admins = db.admins.find({})
    async for admin in admins:
        print(admin)

asyncio.run(main())
