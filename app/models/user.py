from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.resume import Resume
    from app.models.analysis import Analysis
    from app.models.conversation import Conversation


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    full_name: Mapped[str] = mapped_column(String(255))

    password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(), default=None
    )

    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Job.created_at.desc()",
    )

    resumes: Mapped[List["Resume"]] = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Resume.created_at.desc()",
    )

    analyses: Mapped[List["Analysis"]] = relationship(
        "Analysis",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Analysis.created_at.desc()",
    )

    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Conversation.created_at.desc()",
    )
