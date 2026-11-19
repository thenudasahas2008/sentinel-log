import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Index
from app.database import Base

class EventStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"

class EventAction(str, enum.Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    COMMAND = "COMMAND"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    ACCOUNT_CREATION = "ACCOUNT_CREATION"
    ACCOUNT_DELETION = "ACCOUNT_DELETION"
    NETWORK_CONNECTION = "NETWORK_CONNECTION"
    ACCESS_REQUEST = "ACCESS_REQUEST"

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    event_uuid = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    source_ip = Column(String(45), index=True, nullable=True)  # Supports IPv4 and IPv6
    source_port = Column(Integer, nullable=True)
    destination_ip = Column(String(45), index=True, nullable=True)
    destination_port = Column(Integer, nullable=True)
    
    event_type = Column(String(50), index=True, nullable=False)  # e.g., SSH_AUTH, SYS_LOG, WIN_SECURITY, NGINX
    action = Column(String(50), default="LOGIN", nullable=False)
    status = Column(String(20), default="UNKNOWN", index=True, nullable=False)  # SUCCESS, FAILURE, UNKNOWN
    
    username = Column(String(100), index=True, nullable=True)
    hostname = Column(String(100), index=True, nullable=True)
    service = Column(String(50), nullable=True)
    
    raw_log = Column(Text, nullable=False)
    parser_type = Column(String(50), nullable=False)
    import_batch_id = Column(String(64), index=True, nullable=True)
    
    is_synthetic = Column(Boolean, default=False, index=True, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_events_ip_timestamp", "source_ip", "timestamp"),
        Index("idx_events_user_timestamp", "username", "timestamp"),
        Index("idx_events_status_timestamp", "status", "timestamp"),
    )
