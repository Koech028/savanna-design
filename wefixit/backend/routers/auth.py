# backend/routers/auth.py
# backend/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from backend.auth import authenticate_admin, create_access_token
from backend.config import settings
from backend.deps import get_current_admin  # Import from deps.py

router = APIRouter(tags=["auth"])

# Login endpoint
@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_admin(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user["username"])
    return {"access_token": access_token, "token_type": "Bearer"}