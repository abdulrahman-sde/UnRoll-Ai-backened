import logging
import asyncio

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
)
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, register_data: UserRegister) -> UserResponse:
        result = await self.db.execute(
            select(User).where(User.email == register_data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ConflictException(message="User with this email already exists")

        hashed_password = await asyncio.to_thread(
            get_password_hash, register_data.password
        )
        user = User(
            full_name=register_data.full_name,
            email=register_data.email,
            password=hashed_password,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        logger.info("User registered: %s", user.email)
        return UserResponse.model_validate(user)

    async def login(self, credentials: UserLogin) -> UserResponse:
        result = await self.db.execute(
            select(User).where(User.email == credentials.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException(message="Invalid credentials")

        is_valid = await asyncio.to_thread(
            verify_password, credentials.password, user.password
        )
        if not is_valid:
            raise UnauthorizedException(message="Invalid credentials")

        return UserResponse.model_validate(user)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)
