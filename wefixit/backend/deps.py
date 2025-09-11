#deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .auth import decode_token, get_admin_by_username
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    """Validate JWT and return the admin document from MongoDB"""
    username = decode_token(token)
    admin = await get_admin_by_username(username)   # ✅ async Mongo call
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )
    return admin
