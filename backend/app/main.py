import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.api.v1 import api_v1_router
from app.models.user import User, UserRole
from app.models.rule import DetectionRule
from app.utils.security import hash_password
from app.engine.rules import ALL_RULES
from app.utils.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    
    # Seed default users and rules if database is fresh
    db = SessionLocal()
    try:
        # Check admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            logger.info("Seeding default administrative and analyst accounts...")
            admin_user = User(
                username="admin",
                email="admin@sentinellog.local",
                full_name="SOC Administrator",
                hashed_password=hash_password("SentinelAdmin2026!"),
                role=UserRole.ADMIN,
                is_active=True
            )
            analyst_user = User(
                username="analyst",
                email="analyst@sentinellog.local",
                full_name="Lead SOC Analyst",
                hashed_password=hash_password("SentinelAnalyst2026!"),
                role=UserRole.ANALYST,
                is_active=True
            )
            viewer_user = User(
                username="viewer",
                email="auditor@sentinellog.local",
                full_name="Security Auditor",
                hashed_password=hash_password("SentinelViewer2026!"),
                role=UserRole.VIEWER,
                is_active=True
            )
            db.add_all([admin_user, analyst_user, viewer_user])
            db.commit()

        # Seed detection rules metadata
        if db.query(DetectionRule).count() == 0:
            logger.info("Seeding detection rule catalog...")
            for rule_cls in ALL_RULES:
                rule_inst = rule_cls()
                db_rule = DetectionRule(
                    rule_id=rule_inst.rule_id,
                    name=rule_inst.name,
                    description=f"Automated detection rule for {rule_inst.name} adhering to MITRE ATT&CK {rule_inst.mitre_attack_id}",
                    category=rule_inst.category,
                    severity=rule_inst.severity,
                    default_confidence=rule_inst.default_confidence,
                    is_enabled=True,
                    mitre_attack_id=rule_inst.mitre_attack_id
                )
                db.add(db_rule)
            db.commit()

    finally:
        db.close()

    yield
    logger.info("SentinelLog shutdown complete.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced Security Log Intelligence & Threat Detection Platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],  # Permissive for local dev & testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_v1_router)

@app.get("/health", tags=["System Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_v1": "/api/v1"
    }
