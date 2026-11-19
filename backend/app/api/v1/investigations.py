import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.investigation import Investigation, InvestigationNote
from app.models.audit import AuditLog
from app.schemas.investigation import (
    InvestigationCreate, InvestigationUpdate, InvestigationResponse,
    InvestigationNoteCreate, InvestigationNoteResponse
)
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/investigations", tags=["Incident Investigations"])

@router.get("", response_model=List[InvestigationResponse])
def get_investigations(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Investigation)
    if status:
        query = query.filter(Investigation.status == status.upper())
    if severity:
        query = query.filter(Investigation.severity == severity.upper())

    return query.order_by(Investigation.created_at.desc()).offset(offset).limit(limit).all()

@router.post("", response_model=InvestigationResponse)
def create_investigation(
    payload: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    case_num = f"CASE-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    inv = Investigation(
        case_number=case_num,
        title=payload.title,
        description=payload.description,
        severity=payload.severity.upper(),
        status="OPEN",
        lead_analyst_id=current_user.id if current_user else None,
        associated_alert_ids=payload.associated_alert_ids,
        associated_ips=payload.associated_ips,
        associated_users=payload.associated_users
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation_detail(investigation_id: int, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv

@router.patch("/{investigation_id}", response_model=InvestigationResponse)
def update_investigation(
    investigation_id: int,
    payload: InvestigationUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    if payload.title is not None:
        inv.title = payload.title
    if payload.description is not None:
        inv.description = payload.description
    if payload.severity is not None:
        inv.severity = payload.severity.upper()
    if payload.status is not None:
        inv.status = payload.status.upper()
        if inv.status == "CLOSED":
            inv.closed_at = datetime.utcnow()
    if payload.verdict is not None:
        inv.verdict = payload.verdict
    if payload.summary is not None:
        inv.summary = payload.summary
    if payload.associated_alert_ids is not None:
        inv.associated_alert_ids = payload.associated_alert_ids
    if payload.associated_ips is not None:
        inv.associated_ips = payload.associated_ips
    if payload.associated_users is not None:
        inv.associated_users = payload.associated_users

    db.commit()
    db.refresh(inv)
    return inv

@router.post("/{investigation_id}/notes", response_model=InvestigationNoteResponse)
def add_investigation_note(
    investigation_id: int,
    payload: InvestigationNoteCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    author_id = current_user.id if current_user else 1
    note = InvestigationNote(
        investigation_id=inv.id,
        author_id=author_id,
        content=payload.content
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
