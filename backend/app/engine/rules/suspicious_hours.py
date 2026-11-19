from datetime import time
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class SuspiciousHoursRule(BaseDetectionRule):
    rule_id: str = "RULE-006"
    name: str = "Suspicious Off-Hours Successful Authentication"
    category: str = "ANOMALOUS_ACCESS"
    severity: str = "LOW"
    default_confidence: float = 0.70
    mitre_attack_id: str = "T1078"

    # Define off-hours window: 01:00 to 05:00 UTC
    START_HOUR: int = 1
    END_HOUR: int = 5

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        for ev in events:
            if ev.status == "SUCCESS" and ev.username:
                hour = ev.timestamp.hour
                if self.START_HOUR <= hour < self.END_HOUR:
                    is_crit = ev.username.lower() in ConfidenceScorer.CRITICAL_ACCOUNTS
                    severity = "MEDIUM" if is_crit else self.severity

                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=1,
                        is_critical_account=is_crit,
                        is_off_hours=True
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"Off-Hours Login Detected for '{ev.username}' ({ev.timestamp.strftime('%H:%M:%S UTC')})",
                        "category": self.category,
                        "severity": severity,
                        "source_ip": ev.source_ip,
                        "target_username": ev.username,
                        "timestamp": ev.timestamp,
                        "evidence": {
                            "login_hour_utc": hour,
                            "time_str": ev.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "is_critical_account": is_crit,
                            "event_id": ev.event_uuid
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Verify legitimate after-hours business justification with account owner '{ev.username}'.",
                        "confidence_score": confidence
                    })

        return alerts
