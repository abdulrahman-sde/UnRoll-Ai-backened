from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="The user's message")
    conversation_id: int | None = Field(
        default=None,
        description="Existing conversation ID. If null, a new conversation is created.",
    )


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime | None
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime | None
    messages: list[MessageResponse]

    model_config = {"from_attributes": True}
