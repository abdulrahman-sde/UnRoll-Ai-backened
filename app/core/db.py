import contextvars
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Context variable to share the request-scoped DB session with LangGraph tools
_current_db_session: contextvars.ContextVar[AsyncSession | None] = contextvars.ContextVar(
    "_current_db_session", default=None
)


def set_current_session(session: AsyncSession) -> contextvars.Token:
    """Set the current request session so tools can reuse it."""
    return _current_db_session.set(session)


def reset_current_session(token: contextvars.Token) -> None:
    """Reset the context variable after the request."""
    _current_db_session.reset(token)


@asynccontextmanager
async def get_tool_session():
    """Get a DB session for tool use. Reuses the request session if available."""
    existing = _current_db_session.get(None)
    if existing:
        yield existing
    else:
        async with AsyncSessionLocal() as session:
            yield session


# Base class for all models
class Base(DeclarativeBase):
    pass
