from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
import ipaddress
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class SSHBruteForceRule(BaseDetectionRule):
    rule_id: str = "RULE-001"
    name: str = "SSH Authentication Brute-Force Attack"
    category: str = "BRUTE_FORCE"
    severity: str = "HIGH"
    default_confidence: float = 0.85
    mitre_attack_id: str = "T1110.001"

    THRESHOLD: int = 5
    WINDOW_MINUTES: int = 10

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        # Group failed events by source_ip
        ip_failures = defaultdict(list)
        for ev in events:
            if ev.status == "FAILURE" and ev.source_ip:
                ip_failures[ev.source_ip].append(ev)

        for ip, fail_list in ip_failures.items():
            if len(fail_list) < self.THRESHOLD:
                continue

            fail_list.sort(key=lambda x: x.timestamp)
            # Sliding window check
            window = timedelta(minutes=self.WINDOW_MINUTES)
            for i in range(len(fail_list)):
                sub_window = [e for e in fail_list[i:] if (e.timestamp - fail_list[i].timestamp) <= window]
                if len(sub_window) >= self.THRESHOLD:
                    target_users = list({e.username for e in sub_window if e.username})
                    is_crit = any(u.lower() in ConfidenceScorer.CRITICAL_ACCOUNTS for u in target_users)
                    
                    # IP type
                    is_ext = True
                    try:
                        is_ext = not ipaddress.ip_address(ip).is_private
                    except Exception:
                        pass

                    duration_min = max(0.1, (sub_window[-1].timestamp - sub_window[0].timestamp).total_seconds() / 60.0)
                    velocity = len(sub_window) / duration_min

                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=len(sub_window),
                        distinct_users=len(target_users),
                        is_critical_account=is_crit,
                        is_external_ip=is_ext,
                        velocity_per_minute=velocity
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"SSH Brute-Force Attack Detected from {ip}",
                        "category": self.category,
                        "severity": "CRITICAL" if len(sub_window) >= 15 or is_crit else self.severity,
                        "source_ip": ip,
                        "target_username": target_users[0] if len(target_users) == 1 else f"Multiple ({len(target_users)} accounts)",
                        "timestamp": sub_window[-1].timestamp,
                        "evidence": {
                            "failure_count": len(sub_window),
                            "time_window_minutes": self.WINDOW_MINUTES,
                            "first_attempt": sub_window[0].timestamp.isoformat(),
                            "last_attempt": sub_window[-1].timestamp.isoformat(),
                            "targeted_accounts": target_users[:10],
                            "velocity_per_min": round(velocity, 2),
                            "event_ids": [e.event_uuid for e in sub_window[:20]]
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Block IP address {ip} at edge firewall / iptables; enforce fail2ban rate-limiting; review targeted accounts for lockout.",
                        "confidence_score": confidence
                    })
                    break  # One alert per IP batch

        return alerts
