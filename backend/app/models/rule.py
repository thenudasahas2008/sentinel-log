from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, JSON, Float, Text, DateTime
from app.database import Base

class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), index=True, nullable=False)
    severity = Column(String(20), nullable=False)
    default_confidence = Column(Float, default=0.85, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    parameters = Column(JSON, nullable=True)  # custom thresholds, windows
    mitre_attack_id = Column(String(30), nullable=True)  # e.g., T1110.001
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
