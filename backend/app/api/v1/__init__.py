from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.events import router as events_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.investigations import router as investigations_router
from app.api.v1.ip_intel import router as ip_intel_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.reports import router as reports_router
from app.api.v1.users import router as users_router
from app.api.v1.audit import router as audit_router
from app.api.v1.demo import router as demo_router
from app.api.v1.websocket import router as ws_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(investigations_router)
api_v1_router.include_router(ip_intel_router)
api_v1_router.include_router(ingestion_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(demo_router)
api_v1_router.include_router(ws_router)

__all__ = ["api_v1_router"]
