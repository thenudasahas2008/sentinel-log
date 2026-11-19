from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class RepeatedFailuresRule(BaseDetectionRule):
    rule_id: str = "RULE-004"
    name: str = "Targeted Account Repeated Authentication Failures"
    category: str = "ACCOUNT_COMPROMISE"
    severity: str = "MEDIUM"
    default_confidence: float = 0.82
    mitre_attack_id: str = "T1110.001"

    THRESHOLD: int = 8
    WINDOW_MINUTES: int = 15

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        user_failures = defaultdict(list)
        for ev in events:
            if ev.status == "FAILURE" and ev.username:
                user_failures[ev.username].append(ev)

        for user, fail_list in user_failures.items():
            if len(fail_list) < self.THRESHOLD:
                continue

            fail_list.sort(key=lambda x: x.timestamp)
            window = timedelta(minutes=self.WINDOW_MINUTES)

            for i in range(len(fail_list)):
                sub_window = [e for e in fail_list[i:] if (e.timestamp - fail_list[i].timestamp) <= window]
                if len(sub_window) >= self.THRESHOLD:
                    ips = list({e.source_ip for e in sub_window if e.source_ip})
                    is_crit = user.lower() in ConfidenceScorer.CRITICAL_ACCOUNTS

                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=len(sub_window),
                        distinct_users=1,
                        is_critical_account=is_crit,
                        velocity_per_minute=len(sub_window) / (self.WINDOW_MINUTES or 1)
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"Repeated Authentication Failures Targeting Account '{user}'",
                        "category": self.category,
                        "severity": "HIGH" if is_crit else self.severity,
                        "source_ip": ips[0] if len(ips) == 1 else "Multiple IPs",
                        "target_username": user,
                        "timestamp": sub_window[-1].timestamp,
                        "evidence": {
                            "failure_count": len(sub_window),
                            "target_account": user,
                            "source_ips": ips[:10],
                            "time_window_minutes": self.WINDOW_MINUTES,
                            "is_critical_account": is_crit
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Temporarily lock account '{user}' or require immediate MFA verification; examine source IPs for automated attacking scripts.",
                        "confidence_score": confidence
                    })
                    break

        return alerts
