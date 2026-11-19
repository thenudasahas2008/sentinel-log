from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        target_resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        status: str = "SUCCESS"
    ) -> AuditLog:
        record = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            target_resource=target_resource,
            details=details,
            ip_address=ip_address,
            status=status,
            timestamp=datetime.utcnow()
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
