import json
import logging
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import get_agent
from app.core.db import set_current_session, reset_current_session
from app.models.conversation import Conversation, Message
from app.schemas.chat import (
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
)

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 20


class ChatService:
    """Orchestrates chatbot agent invocation with streaming and persistence."""

    def __init__(self, db: AsyncSession):
        self.db = db



    async def stream_message(
        self,
        user_id: int,
        message: str,
        conversation_id: int | None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response as SSE events.

        1. Create or load conversation
        2. Persist user message
        3. Stream LLM response tokens via SSE
        4. Persist complete AI message
        """
        graph = get_agent("chatbot")

        # --- 1. Get or create conversation ---
        if conversation_id:
            conv = await self._get_conversation(conversation_id, user_id)
            if not conv:
                yield f"data: {json.dumps({'type': 'error', 'content': 'Conversation not found'})}\n\n"
                return
        else:
            conv = Conversation(title="New Chat", user_id=user_id)
            self.db.add(conv)
            await self.db.flush()

        # --- 2. Persist user message ---
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=message,
        )
        self.db.add(user_msg)
        await self.db.flush()

        # Send conversation_id immediately so frontend can track multi-turn
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conv.id})}\n\n"

        # --- 3. Build LangChain message history (capped) ---
        lc_messages = []
        if conversation_id and hasattr(conv, "messages"):
            recent = conv.messages[-MAX_HISTORY_MESSAGES:]
            for msg in recent:
                if msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

        if not lc_messages or lc_messages[-1].content != message:
            lc_messages.append(HumanMessage(content=message))

        # --- 4. Stream LLM response ---
        # Share our DB session with tools via contextvars
        ctx_token = set_current_session(self.db)
        full_response = ""

        try:
            async for event in graph.astream_events(
                {"messages": lc_messages, "user_id": user_id},
                version="v2",
            ):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        full_response += chunk.content
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
        except Exception as e:
            logger.exception("Streaming error")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            return
        finally:
            reset_current_session(ctx_token)

        # --- 5. Persist full AI response ---
        if full_response:
            ai_msg = Message(
                conversation_id=conv.id,
                role="assistant",
                content=full_response,
            )
            self.db.add(ai_msg)

            if conv.title == "New Chat":
                conv.title = message[:80] + ("..." if len(message) > 80 else "")

            await self.db.flush()

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    # ------------------------------------------------------------------
    # Conversation CRUD
    # ------------------------------------------------------------------

    async def get_conversations(self, user_id: int) -> list[ConversationResponse]:
        """List all conversations for a user."""
        result = await self.db.execute(
            select(
                Conversation,
                func.count(Message.id).label("message_count"),
            )
            .outerjoin(Message)
            .where(Conversation.user_id == user_id)
            .group_by(Conversation.id)
            .order_by(desc(Conversation.created_at))
        )

        items = []
        for conv, msg_count in result.all():
            items.append(
                ConversationResponse(
                    id=conv.id,
                    title=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=msg_count,
                )
            )
        return items

    async def get_conversation_detail(
        self, conversation_id: int, user_id: int
    ) -> ConversationDetailResponse | None:
        """Get a conversation with all its messages."""
        conv = await self._get_conversation(conversation_id, user_id)
        if not conv:
            return None

        return ConversationDetailResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at,
                )
                for m in conv.messages
            ],
        )

    async def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation and all its messages."""
        conv = await self._get_conversation(conversation_id, user_id)
        if not conv:
            return False
        await self.db.delete(conv)
        await self.db.flush()
        return True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _get_conversation(
        self, conversation_id: int, user_id: int
    ) -> Conversation | None:
        from sqlalchemy.orm import selectinload
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()
