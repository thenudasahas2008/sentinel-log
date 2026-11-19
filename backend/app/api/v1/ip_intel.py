from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ip_service import IPIntelligenceService
from app.schemas.ip_intel import IpIntelligenceResponse

router = APIRouter(prefix="/ip-intel", tags=["IP Intelligence"])

@router.get("/{ip}", response_model=IpIntelligenceResponse)
def lookup_ip_intelligence(ip: str, db: Session = Depends(get_db)):
    result = IPIntelligenceService.inspect_ip(db, ip)
    if not result["is_valid"]:
        raise HTTPException(status_code=400, detail="Invalid IPv4 or IPv6 address")
    return result
