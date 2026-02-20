import logging
import cloudinary
import cloudinary.uploader
import pymupdf
from fastapi import Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.exceptions import NotFoundException, ValidationException
from app.models.analysis import Analysis
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import AnalysisResponse, AnalysisResultSchema
from app.utils.ai import run_analysis

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text")  # type: ignore[assignment]
    doc.close()

    if not text.strip():
        raise ValidationException(
            message="Could not extract text from PDF — the file may be image-based or empty"
        )

    return text.strip()


def upload_to_cloudinary(file_bytes: bytes, filename: str) -> str:
    """Upload PDF bytes to Cloudinary and return the secure URL."""
    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="raw",
        folder="resumes",
        public_id=filename.rsplit(".", 1)[0],  # strip extension for public_id
        overwrite=True,
    )
    return result["secure_url"]


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_analysis(
        self,
        file: UploadFile,
        job_id: int | None,
        user: User,
    ) -> AnalysisResponse:
        """
        Full analysis pipeline:
        1. Upload PDF to Cloudinary → get URL
        2. Parse PDF → extract text
        3. Fetch job title + description (if job_id provided)
        4. Run LangChain analysis
        5. Save resume + analysis to DB
        """
        # --- Read file bytes ---
        file_bytes = await file.read()

        # --- 1. Upload to Cloudinary ---
        logger.info("Uploading resume to Cloudinary: %s", file.filename)
        resume_url = upload_to_cloudinary(file_bytes, file.filename or "resume.pdf")
        logger.info("Resume uploaded: %s", resume_url)

        # --- 2. Parse PDF ---
        logger.info("Parsing PDF: %s", file.filename)
        resume_text = parse_pdf(file_bytes)
        logger.info("Extracted %d characters from PDF", len(resume_text))

        # --- 3. Get job info ---
        job_title = "General Position"
        job_description = (
            "Evaluate this resume for general employability, skills, and experience."
        )

        if job_id is not None:
            result = await self.db.execute(
                select(Job).where(Job.id == job_id, Job.user_id == user.id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise NotFoundException(message=f"Job with id {job_id} not found")
            job_title = job.title
            job_description = job.description

        # --- 4. Save resume to DB ---
        resume = Resume(
            url=resume_url,
            content=resume_text,
            user_id=user.id,
        )
        self.db.add(resume)
        await self.db.flush()  # get resume.id

        # --- 5. Run AI analysis ---
        logger.info("Starting AI analysis...")
        analysis_result: AnalysisResultSchema = await run_analysis(
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_description,
        )

        # --- 6. Save analysis to DB ---
        analysis = Analysis(
            candidate_name=analysis_result.candidate_name,
            target_role=analysis_result.target_role,
            recommendation=analysis_result.recommendation.value,
            overall_score=analysis_result.scores.overall,
            total_experience_years=analysis_result.total_experience_years,
            analysis_result=analysis_result.model_dump(mode="json"),
            user_id=user.id,
            resume_id=resume.id,
            job_id=job_id,
        )
        self.db.add(analysis)
        await self.db.flush()

        logger.info("Analysis saved with id: %d", analysis.id)

        return AnalysisResponse(
            id=analysis.id,
            resume_id=analysis.resume_id,
            job_id=analysis.job_id,
            candidate_name=analysis.candidate_name,
            recommendation=analysis_result.recommendation,
            overall_score=analysis.overall_score,
            total_experience_years=analysis.total_experience_years,
            analysis_result=analysis_result,
            created_at=analysis.created_at,
        )


def get_analysis_service(db: AsyncSession = Depends(get_db)) -> AnalysisService:
    return AnalysisService(db)
