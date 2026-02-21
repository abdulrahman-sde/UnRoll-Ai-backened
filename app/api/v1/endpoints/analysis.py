from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_user, TokenUser
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import AnalysisService, get_analysis_service
from app.utils.utils import success_response

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_analysis(
    body: AnalysisRequest = Depends(),
    current_user: TokenUser = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Run AI analysis on an uploaded resume PDF, optionally matched against a job."""
    body.validate_file()

    result = await service.create_analysis(
        file=body.file,
        job_id=body.job_id,
        user=current_user,
    )

    return success_response(
        message="Analysis completed successfully",
        data=result.model_dump(mode="json"),
    )


@router.get("", status_code=status.HTTP_200_OK)
async def get_analyses(
    job_id: Optional[int] = Query(default=None),
    current_user: TokenUser = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Get all analyses for the authenticated user, optionally filtered by job."""
    analyses = await service.get_analyses_by_user(current_user, job_id=job_id)
    return success_response(
        "Analyses retrieved successfully",
        data=[a.model_dump(mode="json") for a in analyses],
    )


@router.get("/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_analysis_by_id(
    analysis_id: int,
    current_user: TokenUser = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    """Get a single analysis by ID for the authenticated user."""
    analysis = await service.get_analysis_by_id(analysis_id, current_user)
    return success_response(
        "Analysis retrieved successfully",
        data=analysis.model_dump(mode="json"),
    )
