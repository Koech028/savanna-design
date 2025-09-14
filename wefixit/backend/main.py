# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.config import settings
from backend.routers import contacts, reviews, portfolio, auth as auth_router, projects, quotes
from backend.database import db  # ✅ Import your db here

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

    # -------------------- Serve static files --------------------
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    # -------------------- CORS --------------------
    origins = [
        "http://localhost:8080",             # Dev
        "http://127.0.0.1:8080",             # Dev fallback
        "https://savannadesignsagency.com",  # Production HTTPS
        "http://savannadesignsagency.com"    # Production HTTP
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------- API routers --------------------
    app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
    app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
    app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["quotes"])
    app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])

    # -------------------- DB Check endpoint --------------------
    @app.get("/api/v1/db-check", tags=["system"])
    async def db_check():
        try:
            collections = await db.list_collection_names()
            return {"status": "connected", "collections": collections}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    # -------------------- Root endpoint --------------------
    @app.get("/")
    async def root():
        return {"status": "ok", "name": settings.PROJECT_NAME}

    return app

# -------------------- Initialize app --------------------
app = create_app()
