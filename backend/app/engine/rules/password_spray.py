from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
import ipaddress
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class PasswordSprayingRule(BaseDetectionRule):
    rule_id: str = "RULE-002"
    name: str = "Horizontal Password Spraying Pattern"
    category: str = "CREDENTIAL_ACCESS"
    severity: str = "HIGH"
    default_confidence: float = 0.88
    mitre_attack_id: str = "T1110.003"

    USER_THRESHOLD: int = 3
    WINDOW_MINUTES: int = 20

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        ip_events = defaultdict(list)
        for ev in events:
            if ev.status == "FAILURE" and ev.source_ip and ev.username:
                ip_events[ev.source_ip].append(ev)

        for ip, fail_list in ip_events.items():
            fail_list.sort(key=lambda x: x.timestamp)
            window = timedelta(minutes=self.WINDOW_MINUTES)
            
            for i in range(len(fail_list)):
                sub_window = [e for e in fail_list[i:] if (e.timestamp - fail_list[i].timestamp) <= window]
                distinct_users = list({e.username for e in sub_window})
                
                if len(distinct_users) >= self.USER_THRESHOLD:
                    duration_min = max(0.1, (sub_window[-1].timestamp - sub_window[0].timestamp).total_seconds() / 60.0)
                    velocity = len(sub_window) / duration_min
                    
                    is_ext = True
                    try:
                        is_ext = not ipaddress.ip_address(ip).is_private
                    except Exception:
                        pass

                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=len(sub_window),
                        distinct_users=len(distinct_users),
                        is_critical_account=any(u.lower() in ConfidenceScorer.CRITICAL_ACCOUNTS for u in distinct_users),
                        is_external_ip=is_ext,
                        velocity_per_minute=velocity
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"Password Spraying Detected across {len(distinct_users)} Accounts from {ip}",
                        "category": self.category,
                        "severity": self.severity,
                        "source_ip": ip,
                        "target_username": f"{len(distinct_users)} Distinct Users",
                        "timestamp": sub_window[-1].timestamp,
                        "evidence": {
                            "distinct_user_count": len(distinct_users),
                            "targeted_users": distinct_users[:15],
                            "total_failures": len(sub_window),
                            "time_window_minutes": self.WINDOW_MINUTES,
                            "event_ids": [e.event_uuid for e in sub_window[:20]]
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Apply temporary block on IP {ip}; inspect active sessions for targeted accounts; notify Identity & Access team.",
                        "confidence_score": confidence
                    })
                    break

        return alerts
