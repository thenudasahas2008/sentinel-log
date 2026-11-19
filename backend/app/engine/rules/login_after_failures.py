from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class LoginAfterFailuresRule(BaseDetectionRule):
    rule_id: str = "RULE-005"
    name: str = "Successful Authentication Following Multiple Failures"
    category: str = "ACCOUNT_TAKEOVER"
    severity: str = "CRITICAL"
    default_confidence: float = 0.92
    mitre_attack_id: str = "T1078"

    FAILURE_THRESHOLD: int = 3
    WINDOW_MINUTES: int = 15

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        # Group all events by (source_ip, username)
        streams = defaultdict(list)
        for ev in events:
            if ev.source_ip and ev.username:
                streams[(ev.source_ip, ev.username)].append(ev)

        for (ip, user), ev_list in streams.items():
            ev_list.sort(key=lambda x: x.timestamp)
            for idx, ev in enumerate(ev_list):
                if ev.status == "SUCCESS":
                    # Look backwards in window
                    window_start = ev.timestamp - timedelta(minutes=self.WINDOW_MINUTES)
                    prior_failures = [
                        e for e in ev_list[:idx]
                        if e.status == "FAILURE" and e.timestamp >= window_start
                    ]
                    if len(prior_failures) >= self.FAILURE_THRESHOLD:
                        is_crit = user.lower() in ConfidenceScorer.CRITICAL_ACCOUNTS
                        confidence = ConfidenceScorer.calculate_confidence(
                            base_rule_confidence=self.default_confidence,
                            failure_count=len(prior_failures),
                            distinct_users=1,
                            is_critical_account=is_crit
                        )

                        alerts.append({
                            "rule_id": self.rule_id,
                            "title": f"Possible Account Takeover: Successful Login for '{user}' After {len(prior_failures)} Failures",
                            "category": self.category,
                            "severity": self.severity,
                            "source_ip": ip,
                            "target_username": user,
                            "timestamp": ev.timestamp,
                            "evidence": {
                                "prior_failure_count": len(prior_failures),
                                "success_timestamp": ev.timestamp.isoformat(),
                                "first_failure_timestamp": prior_failures[0].timestamp.isoformat(),
                                "delta_seconds": (ev.timestamp - prior_failures[-1].timestamp).total_seconds(),
                                "success_event_id": ev.event_uuid,
                                "failure_event_ids": [f.event_uuid for f in prior_failures[:10]]
                            },
                            "detection_rule_name": self.name,
                            "recommended_action": f"IMMEDIATE ACTION: Terminate active sessions for user '{user}'; force credential reset and check post-login activity on host.",
                            "confidence_score": confidence
                        })
                        break

        return alerts
