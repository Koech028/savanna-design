import asyncio
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://tituskipkoech737:WzrnJuD5ftop7mUE@cluster0.mkf2us5.mongodb.net/wefixit?retryWrites=true&w=majority&appName=Cluster0"

async def test():
    client = AsyncIOMotorClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=20000,
        connectTimeoutMS=20000
    )
    try:
        result = await client.admin.command("ping")
        print("✅ Connected:", result)
    except Exception as e:
        print("❌ Connection failed:", e)

asyncio.run(test())
