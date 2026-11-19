from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class SecurityEventBase(BaseModel):
    timestamp: datetime
    source_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_ip: Optional[str] = None
    destination_port: Optional[int] = None
    event_type: str
    action: str = "LOGIN"
    status: str = "UNKNOWN"
    username: Optional[str] = None
    hostname: Optional[str] = None
    service: Optional[str] = None
    raw_log: str
    parser_type: str
    is_synthetic: bool = False
    metadata_json: Optional[Dict[str, Any]] = None

class SecurityEventCreate(SecurityEventBase):
    pass

class SecurityEventResponse(SecurityEventBase):
    id: int
    event_uuid: str
    created_at: datetime

    class Config:
        from_attributes = True

class EventQueryFilters(BaseModel):
    source_ip: Optional[str] = None
    username: Optional[str] = None
    status: Optional[str] = None
    event_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_synthetic: Optional[bool] = None
    page: int = 1
    page_size: int = 50
