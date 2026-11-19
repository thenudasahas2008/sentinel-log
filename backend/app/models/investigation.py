from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="MEDIUM", nullable=False)
    status = Column(String(30), default="OPEN", index=True, nullable=False)  # OPEN, IN_PROGRESS, CLOSED
    
    lead_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    associated_alert_ids = Column(JSON, default=list)  # List of alert UUIDs
    associated_ips = Column(JSON, default=list)
    associated_users = Column(JSON, default=list)
    
    verdict = Column(String(50), nullable=True)  # TRUE_POSITIVE, FALSE_POSITIVE, BENIGN_ANOMALY
    summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    lead_analyst = relationship("User", back_populates="investigations")
    notes = relationship("InvestigationNote", back_populates="investigation", cascade="all, delete-orphan")

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="notes")
    author = relationship("User")
