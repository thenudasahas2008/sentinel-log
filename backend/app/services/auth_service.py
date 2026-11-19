from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.config import settings

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str, ip_address: Optional[str] = None) -> Optional[User]:
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            # Audit failed login attempt
            audit = AuditLog(
                user_id=None,
                username=username,
                action="USER_LOGIN_FAILED",
                target_resource="AUTH",
                details={"reason": "Invalid credentials or inactive account"},
                ip_address=ip_address,
                status="FAILURE"
            )
            db.add(audit)
            db.commit()
            return None

        if not verify_password(password, user.hashed_password):
            audit = AuditLog(
                user_id=user.id,
                username=username,
                action="USER_LOGIN_FAILED",
                target_resource="AUTH",
                details={"reason": "Password verification mismatch"},
                ip_address=ip_address,
                status="FAILURE"
            )
            db.add(audit)
            db.commit()
            return None

        # Update last login
        user.last_login_at = datetime.utcnow()
        audit = AuditLog(
            user_id=user.id,
            username=username,
            action="USER_LOGIN_SUCCESS",
            target_resource="AUTH",
            details={"role": user.role.value},
            ip_address=ip_address,
            status="SUCCESS"
        )
        db.add(audit)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.ANALYST,
        full_name: Optional[str] = None
    ) -> User:
        hashed = hash_password(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed,
            role=role,
            full_name=full_name,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def generate_tokens(user: User) -> Tuple[str, str]:
        access_token = create_access_token(subject=user.username, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.username)
        return access_token, refresh_token
