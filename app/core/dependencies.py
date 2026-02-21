from dataclasses import dataclass
from typing import AsyncGenerator
from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException


@dataclass
class TokenUser:
    """Lightweight user object decoded from a JWT — no DB query needed."""
    id: int
    email: str


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
) -> TokenUser:
    """Decode the JWT and return a TokenUser — no DB query needed, JWT is self-contained."""
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(message="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = decode_access_token(token)
        return TokenUser(id=payload["user_id"], email=payload["email"])
    except Exception as e:
        if isinstance(e, UnauthorizedException):
            raise
        raise UnauthorizedException(message="Invalid or expired token")
