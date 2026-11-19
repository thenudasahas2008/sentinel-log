from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.models.alert import AlertSeverity, AlertStatus

class AlertBase(BaseModel):
    rule_id: str
    title: str
    category: str
    severity: str
    source_ip: Optional[str] = None
    target_username: Optional[str] = None
    timestamp: datetime
    evidence: Dict[str, Any]
    detection_rule_name: str
    recommended_action: str
    confidence_score: float
    status: str = "NEW"
    is_synthetic: bool = False

class AlertCreate(AlertBase):
    alert_uuid: str

class AlertResponse(AlertBase):
    id: int
    alert_uuid: str
    created_at: datetime
    assigned_to_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True

class AlertUpdateStatus(BaseModel):
    status: AlertStatus
    resolution_notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
