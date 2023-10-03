import time
from fastapi import APIRouter, Response, Depends
from core.dependencies import PermissionDependency, AllowAll
from modules.auth.services import router as auth_router
from modules.users.services import router as user_router
from modules.jobs.services import router as jobs_router
from modules.files.services import router as files_router
from modules.assessments.services import router as assessment_router

router = APIRouter(
     prefix="/api/v1"
)

# Health check endpoint
@router.get("/health", dependencies=[Depends(PermissionDependency([AllowAll]))], tags=["Health-Check"])
async def health_check():
    start_time = time.time()
    process_time = time.time() - start_time
    return {
    "status":"Healthy",
    "totalTimeTaken":str(process_time),
    "entities":[]
}

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(jobs_router)
router.include_router(files_router)
router.include_router(assessment_router)


__all__ = ["router"]