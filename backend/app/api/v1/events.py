from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.event import SecurityEvent
from app.schemas.event import SecurityEventResponse

router = APIRouter(prefix="/events", tags=["Security Events"])

@router.get("", response_model=List[SecurityEventResponse])
def get_security_events(
    source_ip: Optional[str] = None,
    username: Optional[str] = None,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    search: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(SecurityEvent)

    if source_ip:
        query = query.filter(SecurityEvent.source_ip == source_ip.strip())
    if username:
        query = query.filter(SecurityEvent.username.ilike(f"%{username.strip()}%"))
    if status:
        query = query.filter(SecurityEvent.status == status.upper())
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type.upper())
    if start_time:
        query = query.filter(SecurityEvent.timestamp >= start_time)
    if end_time:
        query = query.filter(SecurityEvent.timestamp <= end_time)
    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                SecurityEvent.username.ilike(search_filter),
                SecurityEvent.source_ip.ilike(search_filter),
                SecurityEvent.raw_log.ilike(search_filter),
                SecurityEvent.hostname.ilike(search_filter)
            )
        )

    events = query.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit).all()
    return events

@router.get("/{event_uuid}", response_model=SecurityEventResponse)
def get_event_by_uuid(event_uuid: str, db: Session = Depends(get_db)):
    event = db.query(SecurityEvent).filter(SecurityEvent.event_uuid == event_uuid).first()
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")
    return event
