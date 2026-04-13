"""
Auth routes — register, login, refresh token, get current user, logout.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.base import get_db
from backend.api.schemas.user import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserOut
from backend.api.services.auth_service import register_user, login_user, refresh_tokens
from backend.api.middleware.auth_middleware import get_authenticated_user
from backend.api.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user and return tokens immediately."""
    user = await register_user(data, db)
    from backend.core.security import create_access_token, create_refresh_token
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        user=user,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and receive access + refresh tokens."""
    return await login_user(data, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    return await refresh_tokens(data.refresh_token, db)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_authenticated_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_authenticated_user)):
    """Logout — client should discard tokens. Token blacklist can be added via Redis."""
    return None
