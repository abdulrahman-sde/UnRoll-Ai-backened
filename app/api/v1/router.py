from fastapi import APIRouter
from app.api.v1.endpoints import auth, jobs, analysis

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
router.include_router(analysis.router, prefix="/analyses", tags=["Analyses"])
