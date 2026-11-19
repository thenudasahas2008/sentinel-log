from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class MultiSourceIPRule(BaseDetectionRule):
    rule_id: str = "RULE-007"
    name: str = "Multi-Source IP Concurrent Authentication"
    category: str = "SESSION_ANOMALY"
    severity: str = "MEDIUM"
    default_confidence: float = 0.84
    mitre_attack_id: str = "T1078"

    MIN_DISTINCT_IPS: int = 3
    WINDOW_MINUTES: int = 30

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        user_events = defaultdict(list)
        for ev in events:
            if ev.username and ev.source_ip:
                user_events[ev.username].append(ev)

        for user, ev_list in user_events.items():
            ev_list.sort(key=lambda x: x.timestamp)
            window = timedelta(minutes=self.WINDOW_MINUTES)

            for i in range(len(ev_list)):
                sub_window = [e for e in ev_list[i:] if (e.timestamp - ev_list[i].timestamp) <= window]
                distinct_ips = list({e.source_ip for e in sub_window})

                if len(distinct_ips) >= self.MIN_DISTINCT_IPS:
                    is_crit = user.lower() in ConfidenceScorer.CRITICAL_ACCOUNTS
                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=len(sub_window),
                        distinct_users=1,
                        is_critical_account=is_crit
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"Account '{user}' Active Across {len(distinct_ips)} Distinct IPs in {self.WINDOW_MINUTES}m",
                        "category": self.category,
                        "severity": "HIGH" if is_crit else self.severity,
                        "source_ip": distinct_ips[0],
                        "target_username": user,
                        "timestamp": sub_window[-1].timestamp,
                        "evidence": {
                            "distinct_ips": distinct_ips,
                            "ip_count": len(distinct_ips),
                            "event_count": len(sub_window),
                            "time_window_minutes": self.WINDOW_MINUTES,
                            "sample_event_ids": [e.event_uuid for e in sub_window[:10]]
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Check for credential sharing, proxy rotation, or session hijacking for user '{user}'.",
                        "confidence_score": confidence
                    })
                    break

        return alerts
