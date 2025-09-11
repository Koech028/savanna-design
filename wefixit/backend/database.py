# backend/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import logging

logger = logging.getLogger(__name__)

def create_client():
    try:
        # Try the provided URI directly
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=20000)
        # Trigger connection test
        client.admin.command("ping")
        logger.info("✅ Connected to MongoDB using SRV URI")
        return client
    except Exception as e:
        logger.error(f"❌ SRV URI connection failed: {e}")

        # --- Fallback: try Standard Connection ---
        standard_uri = (
            f"mongodb://{settings.MONGO_URI.split('://')[1]}"
            .replace("mongodb+srv://", "mongodb://")
        )

        try:
            client = AsyncIOMotorClient(standard_uri, serverSelectionTimeoutMS=20000)
            client.admin.command("ping")
            logger.info("✅ Connected to MongoDB using Standard URI fallback")
            return client
        except Exception as e2:
            logger.critical(f"❌ Both SRV and Standard connection failed: {e2}")
            raise e2

client = create_client()
db = client[settings.MONGO_DB]

def get_db():
    return db

