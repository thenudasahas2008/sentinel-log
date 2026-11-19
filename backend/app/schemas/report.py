from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ReportGenerateRequest(BaseModel):
    title: str
    report_type: str = "INCIDENT"  # INCIDENT, EXECUTIVE, AUDIT, THREAT_INTEL
    format: str = "PDF"  # HTML, JSON, CSV, PDF
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    include_synthetic: bool = False
    filters: Optional[Dict[str, Any]] = None

class ReportResponse(BaseModel):
    id: int
    report_uuid: str
    title: str
    report_type: str
    format: str
    file_path: str
    file_size_bytes: int
    generated_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
