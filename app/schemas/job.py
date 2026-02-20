from datetime import datetime
from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
