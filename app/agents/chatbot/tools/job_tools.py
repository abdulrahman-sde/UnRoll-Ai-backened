import json
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from sqlalchemy import select, desc

from app.core.db import get_tool_session
from app.models.job import Job
from app.models.analysis import Analysis


@tool
async def get_all_jobs(state: Annotated[dict, InjectedState]) -> str:
    """Get a list of all job positions created by the current user.
    Returns each job with: id, title, description preview, and creation date.
    Use this when the user asks about their job listings.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        result = await db.execute(
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(desc(Job.created_at))
        )
        jobs = result.scalars().all()

        if not jobs:
            return "No jobs found. The user hasn't created any job positions yet."

        items = []
        for j in jobs:
            items.append({
                "id": j.id,
                "title": j.title,
                "description_preview": j.description[:200] + "..." if len(j.description) > 200 else j.description,
                "created_at": j.created_at.isoformat(),
            })
        return json.dumps(items, indent=2)


@tool
async def get_job_details(job_id: int, state: Annotated[dict, InjectedState]) -> str:
    """Get the full details of a specific job position by its ID.
    Returns the complete job title and description.
    Use this when the user asks about a specific job's requirements.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        result = await db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        )
        job = result.scalar_one_or_none()

        if not job:
            return f"Job with ID {job_id} not found."

        return json.dumps({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "created_at": job.created_at.isoformat(),
        }, indent=2)


@tool
async def get_analyses_for_job(job_id: int, state: Annotated[dict, InjectedState]) -> str:
    """Get all resume analyses linked to a specific job position.
    Returns a summary of each candidate analyzed for this job.
    Use this when the user asks about candidates for a specific role or job.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        job_result = await db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        )
        job = job_result.scalar_one_or_none()

        if not job:
            return f"Job with ID {job_id} not found."

        result = await db.execute(
            select(Analysis)
            .where(Analysis.job_id == job_id, Analysis.user_id == user_id)
            .order_by(desc(Analysis.overall_score))
        )
        analyses = result.scalars().all()

        if not analyses:
            return f"No analyses found for job '{job.title}'."

        items = []
        for a in analyses:
            items.append({
                "id": a.id,
                "candidate_name": a.candidate_name,
                "overall_score": a.overall_score,
                "recommendation": a.recommendation,
                "total_experience_years": a.total_experience_years,
                "created_at": a.created_at.isoformat(),
            })

        return json.dumps({
            "job_title": job.title,
            "total_candidates": len(items),
            "candidates": items,
        }, indent=2)
