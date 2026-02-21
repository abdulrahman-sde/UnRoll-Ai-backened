import json
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from sqlalchemy import select, desc

from app.core.db import get_tool_session
from app.models.analysis import Analysis
from app.models.job import Job


@tool
async def get_all_analyses(state: Annotated[dict, InjectedState]) -> str:
    """Get a summary list of all resume analyses for the current user.
    Returns each analysis with: id, candidate name, target role, overall score, recommendation, and date.
    Use this when the user asks about their analyses, candidates, or overall results.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        result = await db.execute(
            select(Analysis)
            .where(Analysis.user_id == user_id)
            .order_by(desc(Analysis.created_at))
        )
        analyses = result.scalars().all()

        if not analyses:
            return "No analyses found. The user hasn't analyzed any resumes yet."

        items = []
        for a in analyses:
            items.append({
                "id": a.id,
                "candidate_name": a.candidate_name,
                "target_role": a.target_role,
                "overall_score": a.overall_score,
                "recommendation": a.recommendation,
                "job_id": a.job_id,
                "created_at": a.created_at.isoformat(),
            })
        return json.dumps(items, indent=2)


@tool
async def get_analysis_details(analysis_id: int, state: Annotated[dict, InjectedState]) -> str:
    """Get the full detailed analysis for a specific analysis ID.
    Returns complete data including scores, score justifications, skills, experience,
    red flags, key vectors, summary, and recommendation.
    Use this when the user asks for details about a specific candidate or analysis.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        result = await db.execute(
            select(Analysis).where(
                Analysis.id == analysis_id, Analysis.user_id == user_id
            )
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            return f"Analysis with ID {analysis_id} not found."

        data = {
            "id": analysis.id,
            "candidate_name": analysis.candidate_name,
            "target_role": analysis.target_role,
            "overall_score": analysis.overall_score,
            "recommendation": analysis.recommendation,
            "total_experience_years": analysis.total_experience_years,
            "job_id": analysis.job_id,
            "created_at": analysis.created_at.isoformat(),
            "analysis_result": analysis.analysis_result,
        }
        return json.dumps(data, indent=2, default=str)


@tool
async def search_analyses_by_candidate(candidate_name: str, state: Annotated[dict, InjectedState]) -> str:
    """Search analyses by candidate name (partial, case-insensitive match).
    Use this when the user asks about a specific person by name.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        result = await db.execute(
            select(Analysis)
            .where(
                Analysis.user_id == user_id,
                Analysis.candidate_name.ilike(f"%{candidate_name}%"),
            )
            .order_by(desc(Analysis.overall_score))
        )
        analyses = result.scalars().all()

        if not analyses:
            return f"No analyses found for candidate matching '{candidate_name}'."

        items = []
        for a in analyses:
            items.append({
                "id": a.id,
                "candidate_name": a.candidate_name,
                "target_role": a.target_role,
                "overall_score": a.overall_score,
                "recommendation": a.recommendation,
                "created_at": a.created_at.isoformat(),
            })
        return json.dumps(items, indent=2)


@tool
async def get_top_candidates(
    state: Annotated[dict, InjectedState],
    limit: int = 5,
    job_id: int | None = None,
) -> str:
    """Get the top candidates ranked by overall score.
    Optionally filter by job_id to see top candidates for a specific job.
    Use this when the user asks about best candidates or rankings.
    """
    user_id = state["user_id"]

    async with get_tool_session() as db:
        query = select(Analysis).where(Analysis.user_id == user_id)

        if job_id is not None:
            query = query.where(Analysis.job_id == job_id)

        query = query.order_by(desc(Analysis.overall_score)).limit(limit)

        result = await db.execute(query)
        analyses = result.scalars().all()

        if not analyses:
            return "No analyses found."

        items = []
        for rank, a in enumerate(analyses, 1):
            item = {
                "rank": rank,
                "candidate_name": a.candidate_name,
                "target_role": a.target_role,
                "overall_score": a.overall_score,
                "recommendation": a.recommendation,
            }
            if a.job_id:
                job_result = await db.execute(
                    select(Job.title).where(Job.id == a.job_id)
                )
                job_title = job_result.scalar_one_or_none()
                item["job_title"] = job_title or "Unknown"
            items.append(item)

        return json.dumps(items, indent=2)
