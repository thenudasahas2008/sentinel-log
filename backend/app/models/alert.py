import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class AlertSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_uuid = Column(String(64), unique=True, index=True, nullable=False)
    rule_id = Column(String(50), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(100), index=True, nullable=False)  # e.g., AUTH_ANOMALY, BRUTE_FORCE, IMPOSSIBLE_TRAVEL
    severity = Column(String(20), index=True, nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    
    source_ip = Column(String(45), index=True, nullable=True)
    target_username = Column(String(100), index=True, nullable=True)
    
    timestamp = Column(DateTime, index=True, nullable=False)
    evidence = Column(JSON, nullable=False)  # event IDs, counts, time windows, anomaly metrics
    detection_rule_name = Column(String(150), nullable=False)
    recommended_action = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0 with documented calculation
    
    status = Column(String(30), default="NEW", index=True, nullable=False)  # NEW, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    is_synthetic = Column(Boolean, default=False, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    assigned_to = relationship("User", back_populates="assigned_alerts")

    __table_args__ = (
        Index("idx_alerts_sev_time", "severity", "timestamp"),
        Index("idx_alerts_ip_time", "source_ip", "timestamp"),
    )
