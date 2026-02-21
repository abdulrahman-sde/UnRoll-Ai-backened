from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.dependencies import TokenUser, get_current_user, get_db
from app.core.exceptions import NotFoundException
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.utils.utils import success_response
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)


@router.post("/")
async def chat(
    request: ChatRequest,
    user: TokenUser = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Stream AI chatbot response as SSE."""
    return StreamingResponse(
        service.stream_message(
            user_id=user.id,
            message=request.message,
            conversation_id=request.conversation_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations")
async def get_conversations(
    user: TokenUser = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """List all conversations for the authenticated user."""
    conversations = await service.get_conversations(user.id)
    return success_response(
        "Conversations retrieved successfully",
        data=[c.model_dump(mode="json") for c in conversations],
    )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    user: TokenUser = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Get a conversation with all its messages."""
    detail = await service.get_conversation_detail(conversation_id, user.id)
    if not detail:
        raise NotFoundException(message=f"Conversation {conversation_id} not found")
    return success_response(
        "Conversation retrieved successfully",
        data=detail.model_dump(mode="json"),
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user: TokenUser = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Delete a conversation and all its messages."""
    deleted = await service.delete_conversation(conversation_id, user.id)
    if not deleted:
        raise NotFoundException(message=f"Conversation {conversation_id} not found")
    return success_response("Conversation deleted successfully", data=None)
