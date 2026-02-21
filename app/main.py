import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from app.core.config import setup_logging
from app.core.exceptions import AppException
from app.utils.utils import error_response
from app.models import (
    user,
    job,
    resume,
    analysis,
    conversation,
)  # noqa: F401 - ensures models are registered with SQLAlchemy


app = FastAPI(title="Unroll Ai Backend", description="Backend API for Unroll AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Unroll Ai", "success": True}


# Setup logging ONCE at application startup
setup_logging()

# Get logger for main module
logger = logging.getLogger(__name__)  # Name will be "__main__"


@app.on_event("startup")
async def startup():
    from app.agents.registry import startup_agents
    startup_agents()
    logger.info("Application starting up — agents registered")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_response(
        message=exc.message, errors=exc.errors, status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {err["loc"][-1]: err["msg"] for err in exc.errors()}
    return error_response("Validation Error", errors=errors, status_code=422)
