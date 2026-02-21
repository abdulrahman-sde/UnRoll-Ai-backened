from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user, TokenUser
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import JobService, get_job_service
from app.utils.utils import success_response

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: TokenUser = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Create a new job for the authenticated user."""
    job = await job_service.create_job(job_data, current_user)
    return success_response("Job created successfully", data=job)


@router.get("", status_code=status.HTTP_200_OK)
async def get_jobs_by_user(
    current_user: TokenUser = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get all jobs for the authenticated user."""
    jobs = await job_service.get_jobs_by_user(current_user)
    return success_response("Jobs retrieved successfully", data=jobs)


@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_job_by_id(
    job_id: int,
    current_user: TokenUser = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    """Get a job by ID for the authenticated user."""
    job = await job_service.get_job_by_id(job_id, current_user)
    return success_response("Job retrieved successfully", data=job)
