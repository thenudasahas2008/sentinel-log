from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class CredentialStuffingRule(BaseDetectionRule):
    rule_id: str = "RULE-003"
    name: str = "Automated Credential Stuffing Campaign"
    category: str = "CREDENTIAL_ACCESS"
    severity: str = "CRITICAL"
    default_confidence: float = 0.90
    mitre_attack_id: str = "T1110.004"

    MIN_FAILURES: int = 15
    MIN_USERS: int = 5
    WINDOW_MINUTES: int = 15

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        ip_events = defaultdict(list)
        for ev in events:
            if ev.status == "FAILURE" and ev.source_ip:
                ip_events[ev.source_ip].append(ev)

        for ip, fail_list in ip_events.items():
            if len(fail_list) < self.MIN_FAILURES:
                continue

            fail_list.sort(key=lambda x: x.timestamp)
            window = timedelta(minutes=self.WINDOW_MINUTES)
            
            for i in range(len(fail_list)):
                sub_window = [e for e in fail_list[i:] if (e.timestamp - fail_list[i].timestamp) <= window]
                users = [e.username for e in sub_window if e.username]
                distinct_users = set(users)

                if len(sub_window) >= self.MIN_FAILURES and len(distinct_users) >= self.MIN_USERS:
                    # Calculate intervals to detect automated bot cadence
                    intervals = []
                    for k in range(1, len(sub_window)):
                        intervals.append((sub_window[k].timestamp - sub_window[k-1].timestamp).total_seconds())
                    avg_interval = sum(intervals) / max(1, len(intervals))

                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=len(sub_window),
                        distinct_users=len(distinct_users),
                        velocity_per_minute=len(sub_window) / (self.WINDOW_MINUTES or 1)
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"High-Velocity Credential Stuffing Campaign from {ip}",
                        "category": self.category,
                        "severity": self.severity,
                        "source_ip": ip,
                        "target_username": f"{len(distinct_users)} Dumped Accounts",
                        "timestamp": sub_window[-1].timestamp,
                        "evidence": {
                            "attempt_count": len(sub_window),
                            "targeted_accounts_count": len(distinct_users),
                            "average_cadence_seconds": round(avg_interval, 2),
                            "is_bot_pattern": avg_interval < 2.0,
                            "time_window_minutes": self.WINDOW_MINUTES,
                            "sample_accounts": list(distinct_users)[:10]
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Deploy WAF credential-stuffing mitigation, challenge or block source IP {ip}, enforce MFA globally for affected user pool.",
                        "confidence_score": confidence
                    })
                    break

        return alerts
