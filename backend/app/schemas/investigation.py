from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel

class InvestigationNoteCreate(BaseModel):
    content: str

class InvestigationNoteResponse(BaseModel):
    id: int
    author_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class InvestigationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "MEDIUM"
    associated_alert_ids: List[str] = []
    associated_ips: List[str] = []
    associated_users: List[str] = []

class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    verdict: Optional[str] = None
    summary: Optional[str] = None
    lead_analyst_id: Optional[int] = None
    associated_alert_ids: Optional[List[str]] = None
    associated_ips: Optional[List[str]] = None
    associated_users: Optional[List[str]] = None

class InvestigationResponse(BaseModel):
    id: int
    case_number: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    lead_analyst_id: Optional[int] = None
    associated_alert_ids: List[str] = []
    associated_ips: List[str] = []
    associated_users: List[str] = []
    verdict: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    notes: List[InvestigationNoteResponse] = []

    class Config:
        from_attributes = True
