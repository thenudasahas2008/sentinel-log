from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class IpReputationHistory(BaseModel):
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    total_events: int = 0
    failed_attempts: int = 0
    successful_attempts: int = 0
    total_alerts: int = 0
    critical_alerts: int = 0

class IpIntelligenceResponse(BaseModel):
    ip: str
    is_valid: bool
    version: int  # 4 or 6
    is_private: bool
    is_loopback: bool
    is_multicast: bool
    threat_score: int  # 0 to 100
    classification: str  # BENIGN, SUSPICIOUS, HIGH_RISK, UNKNOWN
    reputation_history: IpReputationHistory
    targeted_accounts: List[str]
    detected_rules: List[str]
    external_intel: Optional[Dict[str, Any]] = None
