from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class AbnormalFailureSpikeRule(BaseDetectionRule):
    rule_id: str = "RULE-010"
    name: str = "Volumetric Authentication Failure Surge"
    category: str = "VOLUMETRIC_ATTACK"
    severity: str = "HIGH"
    default_confidence: float = 0.89
    mitre_attack_id: str = "T1499"

    THRESHOLD_PER_MINUTE: int = 20

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        failures = [e for e in events if e.status == "FAILURE"]
        if len(failures) < self.THRESHOLD_PER_MINUTE:
            return alerts

        failures.sort(key=lambda x: x.timestamp)
        window = timedelta(minutes=1)

        for i in range(len(failures)):
            sub_window = [e for e in failures[i:] if (e.timestamp - failures[i].timestamp) <= window]
            if len(sub_window) >= self.THRESHOLD_PER_MINUTE:
                ips = list({e.source_ip for e in sub_window if e.source_ip})
                users = list({e.username for e in sub_window if e.username})

                confidence = ConfidenceScorer.calculate_confidence(
                    base_rule_confidence=self.default_confidence,
                    failure_count=len(sub_window),
                    distinct_users=len(users),
                    velocity_per_minute=float(len(sub_window))
                )

                alerts.append({
                    "rule_id": self.rule_id,
                    "title": f"Volumetric Failure Surge: {len(sub_window)} Failures in 60s Across {len(ips)} IPs",
                    "category": self.category,
                    "severity": self.severity,
                    "source_ip": ips[0] if len(ips) == 1 else "Multiple Sources",
                    "target_username": f"{len(users)} Targeted Accounts",
                    "timestamp": sub_window[-1].timestamp,
                    "evidence": {
                        "failures_in_window": len(sub_window),
                        "window_duration_seconds": 60,
                        "unique_sources": len(ips),
                        "unique_targets": len(users),
                        "top_ips": ips[:5],
                        "top_users": users[:5]
                    },
                    "detection_rule_name": self.name,
                    "recommended_action": "Engage rate limiting and perimeter DDoS / bot mitigation; examine edge traffic logs for coordinated botnet activity.",
                    "confidence_score": confidence
                })
                break

        return alerts
