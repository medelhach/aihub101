from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.models import router as models_router
from app.api.routes.operations import router as operations_router
from app.api.routes.publishing import router as publishing_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(publishing_router)
api_router.include_router(models_router)
api_router.include_router(operations_router)
