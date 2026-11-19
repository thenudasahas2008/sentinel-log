import ipaddress
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.event import SecurityEvent
from app.models.alert import Alert
from app.config import settings

class IPIntelligenceService:
    @staticmethod
    def inspect_ip(db: Session, ip_str: str) -> Dict[str, Any]:
        """
        Classifies and analyzes IP address without making assumptions.
        Never labels an IP malicious merely because it is suspicious.
        """
        ip_clean = ip_str.strip().strip("[]").split(":")[0] if "." in ip_str and ":" in ip_str and ip_str.count(":") == 1 else ip_str.strip().strip("[]")
        
        try:
            ip_obj = ipaddress.ip_address(ip_clean)
            is_valid = True
            version = ip_obj.version
            is_private = ip_obj.is_private
            is_loopback = ip_obj.is_loopback
            is_multicast = ip_obj.is_multicast
        except ValueError:
            return {
                "ip": ip_str,
                "is_valid": False,
                "version": 4,
                "is_private": False,
                "is_loopback": False,
                "is_multicast": False,
                "threat_score": 0,
                "classification": "UNKNOWN",
                "reputation_history": {
                    "first_seen": None,
                    "last_seen": None,
                    "total_events": 0,
                    "failed_attempts": 0,
                    "successful_attempts": 0,
                    "total_alerts": 0,
                    "critical_alerts": 0
                },
                "targeted_accounts": [],
                "detected_rules": [],
                "external_intel": None
            }

        # Query local database events for this IP
        events = db.query(SecurityEvent).filter(SecurityEvent.source_ip == ip_clean).all()
        alerts = db.query(Alert).filter(Alert.source_ip == ip_clean).all()

        total_events = len(events)
        failed_attempts = sum(1 for e in events if e.status == "FAILURE")
        successful_attempts = sum(1 for e in events if e.status == "SUCCESS")
        total_alerts = len(alerts)
        critical_alerts = sum(1 for a in alerts if a.severity in ["CRITICAL", "HIGH"])

        first_seen = min((e.timestamp for e in events), default=None)
        last_seen = max((e.timestamp for e in events), default=None)

        targeted_accounts = list({e.username for e in events if e.username})
        detected_rules = list({a.detection_rule_name for a in alerts})

        # Calculate empirical local Threat Score (0 - 100)
        # Based strictly on verifiable local security signals
        score = 0
        if critical_alerts > 0:
            score += min(50, critical_alerts * 20)
        if total_alerts > 0:
            score += min(20, total_alerts * 5)
        if failed_attempts >= 10:
            score += min(20, (failed_attempts // 5) * 5)
        if not is_private and not is_loopback and failed_attempts > 0:
            score += 10

        score = max(0, min(100, score))

        classification = "BENIGN"
        if score >= 75:
            classification = "HIGH_RISK"
        elif score >= 40:
            classification = "SUSPICIOUS"
        elif is_private or is_loopback:
            classification = "LOCAL_INTERNAL"

        # Optional external threat intel (disabled by default)
        external_data = None
        if settings.ENABLE_EXTERNAL_THREAT_INTEL:
            external_data = {
                "source": "Disabled by policy",
                "status": "Inactive"
            }

        return {
            "ip": ip_clean,
            "is_valid": is_valid,
            "version": version,
            "is_private": is_private,
            "is_loopback": is_loopback,
            "is_multicast": is_multicast,
            "threat_score": score,
            "classification": classification,
            "reputation_history": {
                "first_seen": first_seen,
                "last_seen": last_seen,
                "total_events": total_events,
                "failed_attempts": failed_attempts,
                "successful_attempts": successful_attempts,
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts
            },
            "targeted_accounts": targeted_accounts[:15],
            "detected_rules": detected_rules,
            "external_intel": external_data
        }
