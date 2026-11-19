from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("")
def list_audit_logs(
    action: Optional[str] = None,
    username: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action.upper())
    if username:
        query = query.filter(AuditLog.username.ilike(f"%{username}%"))

    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    return logs
