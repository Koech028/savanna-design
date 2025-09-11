# test_connection.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://tituskipkoech737:<password>@cluster0.mkf2us5.mongodb.net/wefixit?retryWrites=true&w=majority&tls=true"

async def test():
    client = AsyncIOMotorClient(MONGO_URI)
    print(await client.admin.command("ping"))

asyncio.run(test())
