from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse
from sqlalchemy import select


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, job_data: JobCreate, user: User) -> JobResponse:
        """Create a new job for the authenticated user."""
        job = Job(
            title=job_data.title,
            description=job_data.description,
            user_id=user.id,
        )
        self.db.add(job)
        await self.db.flush()

        return JobResponse.model_validate(job)

    async def get_jobs_by_user(self, user: User) -> list[JobResponse]:
        """Get all jobs for the authenticated user."""
        jobs = await self.db.execute(select(Job).where(Job.user_id == user.id))
        return [JobResponse.model_validate(job) for job in jobs.scalars().all()]

    async def get_job_by_id(self, job_id: int, user: User) -> JobResponse:
        """Get a job by ID for the authenticated user."""
        job = await self.db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user.id)
        )
        return JobResponse.model_validate(job.scalar_one())


def get_job_service(db: AsyncSession = Depends(get_db)) -> JobService:
    return JobService(db)
