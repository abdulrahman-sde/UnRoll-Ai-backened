from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Float, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.job import Job


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    # Candidate identity (for quick SQL search)
    candidate_name: Mapped[str] = mapped_column(String(255), index=True)

    # Target and Recommendations (for quick SQL filtering)
    target_role: Mapped[str] = mapped_column(String(255))
    recommendation: Mapped[str] = mapped_column(
        String(50), index=True
    )  # "HIRE" | "CONSIDER" | "REJECT"

    # Scores (for quick SQL ordering/filtering)
    overall_score: Mapped[int] = mapped_column(Integer, index=True)
    total_experience_years: Mapped[float] = mapped_column(Float, index=True)

    # Full data storage
    analysis_result: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(), default=None
    )

    # Relationships
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[int | None] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="analyses")
    resume: Mapped["Resume"] = relationship("Resume", back_populates="analyses")
    job: Mapped["Job"] = relationship("Job", back_populates="analyses")
