from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from fastapi import File, Form, UploadFile


# --- Enums ---


class Recommendation(str, Enum):
    HIRE = "HIRE"
    CONSIDER = "CONSIDER"
    REJECT = "REJECT"


class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Confidence(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class RedFlagType(str, Enum):
    EMPLOYMENT_GAP = "employment_gap"
    JOB_HOPPING = "job_hopping"
    UNVERIFIABLE_CLAIM = "unverifiable_claim"
    INCONSISTENT_DATES = "inconsistent_dates"


# --- Sub schemas ---


class ContactDetails(BaseModel):
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    extraction_confidence: Confidence


class EducationItem(BaseModel):
    degree: str
    institution: str
    graduation_year: int | None = None
    gpa: float | None = None


class ScoreBreakdown(BaseModel):
    overall: int
    experience: int
    projects: int
    tech: int
    education: int

    @field_validator("overall", "experience", "projects", "tech", "education")
    @classmethod
    def must_be_valid_score(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {v}")
        return v


class ScoreJustification(BaseModel):
    experience: str
    projects: str
    tech: str
    education: str


class SkillItem(BaseModel):
    name: str
    years: float
    level: int

    @field_validator("level")
    @classmethod
    def valid_level(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError(f"Skill level must be 0-100, got {v}")
        return v


class ExperienceItem(BaseModel):
    title: str
    company: str
    start_year: int
    end_year: int | None = None
    duration_years: float
    match_percentage: int
    description: str

    @field_validator("match_percentage")
    @classmethod
    def valid_match(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError(f"Match percentage must be 0-100, got {v}")
        return v


class RedFlag(BaseModel):
    type: RedFlagType
    description: str
    severity: Severity


class ExtractionStatus(BaseModel):
    personal_info: bool
    education: bool
    experience: bool
    skills: bool
    projects: bool


# --- Main analysis schema ---


class AnalysisResultSchema(BaseModel):
    """The full detailed analysis output from AI"""

    candidate_name: str
    contact: ContactDetails
    education: list[EducationItem]
    total_experience_years: float
    target_role: str

    scores: ScoreBreakdown
    score_justification: ScoreJustification
    recommendation: Recommendation

    summary: str
    shortlist_summary: str
    key_vectors: list[str] = Field(min_length=3, max_length=5)

    skills: list[SkillItem]
    experience: list[ExperienceItem]

    red_flags: list[RedFlag]
    extraction_status: ExtractionStatus


# --- API schemas ---


@dataclass
class AnalysisRequest:
    """
    Multipart form input for POST /analyses.
    Inject via Depends(AnalysisRequest) — FastAPI resolves File + Form fields automatically.
    """

    file: UploadFile = File(..., description="Resume PDF")
    job_id: int | None = Form(
        default=None, description="Optional job ID to match against"
    )

    def validate_file(self) -> None:
        if self.file.content_type != "application/pdf":
            raise ValueError(
                f"Only PDF files are accepted, got: {self.file.content_type}"
            )


class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int | None

    # flattened for frontend convenience
    candidate_name: str
    recommendation: Recommendation
    overall_score: int
    total_experience_years: float

    # full detail
    analysis_result: AnalysisResultSchema

    created_at: datetime

    model_config = {"from_attributes": True}
