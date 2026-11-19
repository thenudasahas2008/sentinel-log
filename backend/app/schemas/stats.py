from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ThreatTimelinePoint(BaseModel):
    timestamp: str
    total_events: int
    failed_logins: int
    critical_alerts: int
    high_alerts: int

class AttackDistributionItem(BaseModel):
    category: str
    count: int
    percentage: float

class TopTargetItem(BaseModel):
    username: str
    attempt_count: int
    failure_count: int
    status: str

class TopSuspiciousIpItem(BaseModel):
    ip: str
    failure_count: int
    alert_count: int
    highest_severity: str
    is_private: bool

class DashboardStats(BaseModel):
    total_events: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    suspicious_ips_count: int
    failed_auth_count: int
    successful_logins_count: int
    active_investigations: int
    timeline: List[ThreatTimelinePoint]
    attack_distribution: List[AttackDistributionItem]
    top_targeted_accounts: List[TopTargetItem]
    top_suspicious_ips: List[TopSuspiciousIpItem]
