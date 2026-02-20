from datetime import datetime
from typing import TYPE_CHECKING, List
from app.core.db import Base
from sqlalchemy import Text, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.analysis import Analysis


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    url: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(), default=None
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user: Mapped["User"] = relationship("User", back_populates="resumes", lazy="joined")
    analyses: Mapped[List["Analysis"]] = relationship(
        "Analysis",
        back_populates="resume",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
