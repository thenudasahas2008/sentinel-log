from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.alert import Alert
from app.models.audit import AuditLog
from app.schemas.alert import AlertResponse, AlertUpdateStatus
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["Threat Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    source_ip: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity.upper())
    if status:
        query = query.filter(Alert.status == status.upper())
    if category:
        query = query.filter(Alert.category == category.upper())
    if source_ip:
        query = query.filter(Alert.source_ip == source_ip.strip())

    alerts = query.order_by(Alert.timestamp.desc()).offset(offset).limit(limit).all()
    return alerts

@router.get("/{alert_uuid}", response_model=AlertResponse)
def get_alert_by_uuid(alert_uuid: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.alert_uuid == alert_uuid).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_uuid}/status", response_model=AlertResponse)
def update_alert_status(
    alert_uuid: str,
    payload: AlertUpdateStatus,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.alert_uuid == alert_uuid).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = payload.status.value
    if payload.resolution_notes:
        alert.resolution_notes = payload.resolution_notes
    if payload.assigned_to_id:
        alert.assigned_to_id = payload.assigned_to_id
    if payload.status.value in ["RESOLVED", "FALSE_POSITIVE"]:
        alert.resolved_at = datetime.utcnow()

    # Audit log
    audit = AuditLog(
        user_id=current_user.id if current_user else None,
        username=current_user.username if current_user else "analyst",
        action="ALERT_STATUS_UPDATE",
        target_resource=alert.alert_uuid,
        details={"new_status": alert.status, "notes": payload.resolution_notes},
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    return alert
