from datetime import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


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
