from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

FullName = Annotated[Optional[str], Field(default=None, max_length=100)]
Password = Annotated[
    str,
    Field(
        min_length=8,
        max_length=100,
    ),
]


class UserBase(BaseModel):
    email: EmailStr
    full_name: FullName


class UserRegister(UserBase):
    password: Password


class UserLogin(BaseModel):
    email: EmailStr
    password: Password


class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}
