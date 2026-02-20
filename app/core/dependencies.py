from typing import AsyncGenerator
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the user from the JWT token."""
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(message="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            raise UnauthorizedException(message="Invalid token payload")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException(message="User not found")

        return user
    except Exception as e:
        if isinstance(e, UnauthorizedException):
            raise
        raise UnauthorizedException(message="Invalid or expired token")
