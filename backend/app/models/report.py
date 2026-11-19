from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_uuid = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # INCIDENT, EXECUTIVE, AUDIT, THREAT_INTEL
    format = Column(String(10), nullable=False)  # HTML, JSON, CSV, PDF
    file_path = Column(String(300), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    parameters = Column(JSON, nullable=True)
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    generated_by = relationship("User")
