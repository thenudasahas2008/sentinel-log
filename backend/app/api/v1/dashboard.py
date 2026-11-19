from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.event import SecurityEvent
from app.models.alert import Alert
from app.models.investigation import Investigation
from app.schemas.stats import (
    DashboardStats, ThreatTimelinePoint, AttackDistributionItem,
    TopTargetItem, TopSuspiciousIpItem
)
import ipaddress

router = APIRouter(prefix="/dashboard", tags=["SOC Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_events = db.query(func.count(SecurityEvent.id)).scalar() or 0
    failed_auth_count = db.query(func.count(SecurityEvent.id)).filter(SecurityEvent.status == "FAILURE").scalar() or 0
    successful_logins_count = db.query(func.count(SecurityEvent.id)).filter(SecurityEvent.status == "SUCCESS").scalar() or 0

    critical_alerts = db.query(func.count(Alert.id)).filter(Alert.severity == "CRITICAL").scalar() or 0
    high_alerts = db.query(func.count(Alert.id)).filter(Alert.severity == "HIGH").scalar() or 0
    medium_alerts = db.query(func.count(Alert.id)).filter(Alert.severity == "MEDIUM").scalar() or 0

    active_investigations = db.query(func.count(Investigation.id)).filter(Investigation.status != "CLOSED").scalar() or 0

    # Suspicious IPs count
    suspicious_ips_query = db.query(Alert.source_ip).filter(Alert.source_ip != None).distinct()
    suspicious_ips_count = suspicious_ips_query.count()

    # Timeline (last 24 hours grouped by 2-hour buckets)
    now = datetime.utcnow()
    timeline: List[ThreatTimelinePoint] = []
    for b in range(12, 0, -1):
        bucket_start = now - timedelta(hours=b * 2)
        bucket_end = now - timedelta(hours=(b - 1) * 2)
        
        events_in_b = db.query(func.count(SecurityEvent.id)).filter(
            SecurityEvent.timestamp >= bucket_start,
            SecurityEvent.timestamp < bucket_end
        ).scalar() or 0

        failures_in_b = db.query(func.count(SecurityEvent.id)).filter(
            SecurityEvent.timestamp >= bucket_start,
            SecurityEvent.timestamp < bucket_end,
            SecurityEvent.status == "FAILURE"
        ).scalar() or 0

        crit_in_b = db.query(func.count(Alert.id)).filter(
            Alert.timestamp >= bucket_start,
            Alert.timestamp < bucket_end,
            Alert.severity == "CRITICAL"
        ).scalar() or 0

        high_in_b = db.query(func.count(Alert.id)).filter(
            Alert.timestamp >= bucket_start,
            Alert.timestamp < bucket_end,
            Alert.severity == "HIGH"
        ).scalar() or 0

        timeline.append(ThreatTimelinePoint(
            timestamp=bucket_end.strftime("%H:%M"),
            total_events=events_in_b,
            failed_logins=failures_in_b,
            critical_alerts=crit_in_b,
            high_alerts=high_in_b
        ))

    # Attack Category Distribution
    category_counts = db.query(Alert.category, func.count(Alert.id)).group_by(Alert.category).all()
    total_alerts = sum(c[1] for c in category_counts) or 1
    attack_distribution = [
        AttackDistributionItem(
            category=cat or "UNKNOWN",
            count=count,
            percentage=round((count / total_alerts) * 100, 1)
        )
        for cat, count in category_counts
    ]

    # Top Targeted Accounts
    top_targets_raw = (
        db.query(SecurityEvent.username, func.count(SecurityEvent.id))
        .filter(SecurityEvent.username != None)
        .group_by(SecurityEvent.username)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(6)
        .all()
    )
    top_targeted_accounts = []
    for uname, total in top_targets_raw:
        fail_c = db.query(func.count(SecurityEvent.id)).filter(
            SecurityEvent.username == uname,
            SecurityEvent.status == "FAILURE"
        ).scalar() or 0
        top_targeted_accounts.append(TopTargetItem(
            username=uname,
            attempt_count=total,
            failure_count=fail_c,
            status="CRITICAL" if fail_c >= 10 else ("WARN" if fail_c >= 4 else "NORMAL")
        ))

    # Top Suspicious IPs
    top_ips_raw = (
        db.query(SecurityEvent.source_ip, func.count(SecurityEvent.id))
        .filter(SecurityEvent.source_ip != None)
        .group_by(SecurityEvent.source_ip)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(6)
        .all()
    )
    top_suspicious_ips = []
    for ip_str, total in top_ips_raw:
        fail_c = db.query(func.count(SecurityEvent.id)).filter(
            SecurityEvent.source_ip == ip_str,
            SecurityEvent.status == "FAILURE"
        ).scalar() or 0
        alert_c = db.query(func.count(Alert.id)).filter(Alert.source_ip == ip_str).scalar() or 0
        
        is_priv = False
        try:
            is_priv = ipaddress.ip_address(ip_str).is_private
        except Exception:
            pass

        highest_sev = "INFO"
        if alert_c > 0:
            crit_c = db.query(func.count(Alert.id)).filter(Alert.source_ip == ip_str, Alert.severity == "CRITICAL").scalar() or 0
            high_c = db.query(func.count(Alert.id)).filter(Alert.source_ip == ip_str, Alert.severity == "HIGH").scalar() or 0
            if crit_c > 0:
                highest_sev = "CRITICAL"
            elif high_c > 0:
                highest_sev = "HIGH"
            else:
                highest_sev = "MEDIUM"

        top_suspicious_ips.append(TopSuspiciousIpItem(
            ip=ip_str,
            failure_count=fail_c,
            alert_count=alert_c,
            highest_severity=highest_sev,
            is_private=is_priv
        ))

    return DashboardStats(
        total_events=total_events,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        medium_alerts=medium_alerts,
        suspicious_ips_count=suspicious_ips_count,
        failed_auth_count=failed_auth_count,
        successful_logins_count=successful_logins_count,
        active_investigations=active_investigations,
        timeline=timeline,
        attack_distribution=attack_distribution,
        top_targeted_accounts=top_targeted_accounts,
        top_suspicious_ips=top_suspicious_ips
    )
