from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import AnalysisService, get_analysis_service
from app.utils.utils import success_response

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_analysis(
    body: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
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
