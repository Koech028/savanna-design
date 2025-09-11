#backend/config.py
import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings(BaseModel):
    # Project info
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "WeFixIt API")
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-super-secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Database (MongoDB)
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "wefixit")

    # Optional: SQLite fallback (if you ever want hybrid or testing db)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wefixit.db")

    # CORS
    CORS_ORIGINS: List[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")
    ]

    # Admin bootstrap (first-time setup only)
    BOOTSTRAP_ADMIN_USERNAME: str = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    BOOTSTRAP_ADMIN_PASSWORD: str = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123")

    class Config:
        case_sensitive = True


# Initialize settings object
settings = Settings()
