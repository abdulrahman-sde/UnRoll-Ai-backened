from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from app.core.config import settings

pwd_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return pwd_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hash.verify(plain_password, hashed_password)


def create_access_token(payload: Dict[str, Any]) -> str:
    to_encode = payload.copy()
    # Use timezone-aware UTC datetime for exp claim
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM or "HS256"
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT, returning the payload."""
    algorithm = settings.ALGORITHM or "HS256"
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[algorithm])
