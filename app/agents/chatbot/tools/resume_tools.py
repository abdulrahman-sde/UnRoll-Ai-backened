import json
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from sqlalchemy import select, desc

from app.core.db import get_tool_session
from app.models.resume import Resume


@tool
async def get_all_resumes(state: Annotated[dict, InjectedState]) -> str:
    """Get a list of all uploaded resumes for the current user.
    Returns each resume with: id, url, content preview (first 200 chars), and upload date.
    Use this when the user asks about their uploaded resumes.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        result = await db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(desc(Resume.created_at))
        )
        resumes = result.scalars().all()

        if not resumes:
            return "No resumes found. The user hasn't uploaded any resumes yet."

        items = []
        for r in resumes:
            items.append({
                "id": r.id,
                "url": r.url,
                "content_preview": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                "created_at": r.created_at.isoformat(),
            })
        return json.dumps(items, indent=2)


@tool
async def get_resume_content(resume_id: int, state: Annotated[dict, InjectedState]) -> str:
    """Get the full extracted text content of a specific resume by its ID.
    Use this when the user wants to see the actual content of a resume,
    or when you need the resume text to answer questions about it.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        result = await db.execute(
            select(Resume).where(
                Resume.id == resume_id, Resume.user_id == user_id
            )
        )
        resume = result.scalar_one_or_none()

        if not resume:
            return f"Resume with ID {resume_id} not found."

        return json.dumps({
            "id": resume.id,
            "url": resume.url,
            "content": resume.content,
            "created_at": resume.created_at.isoformat(),
        }, indent=2)
