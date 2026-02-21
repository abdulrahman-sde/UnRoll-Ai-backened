import asyncio
from app.core.db import AsyncSessionLocal
from app.services.chat_service import ChatService
from app.agents.registry import startup_agents
import app.models.user  # So SQLAlchemy knows about it

async def main():
    startup_agents()
    async with AsyncSessionLocal() as db:
        service = ChatService(db)
        try:
            res = await service.send_message(user_id=1, message="hello", conversation_id=None)
            print("SUCCESS:", res)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(main())
