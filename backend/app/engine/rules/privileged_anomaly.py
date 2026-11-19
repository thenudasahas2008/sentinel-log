import ipaddress
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class PrivilegedAccountAnomalyRule(BaseDetectionRule):
    rule_id: str = "RULE-009"
    name: str = "Direct Remote Privileged Account Authentication"
    category: str = "PRIVILEGED_ACCESS"
    severity: str = "HIGH"
    default_confidence: float = 0.86
    mitre_attack_id: str = "T1078.001"

    PRIVILEGED_USERS = {"root", "administrator", "admin", "system", "postgres", "sa", "oracle"}

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        for ev in events:
            if ev.status == "SUCCESS" and ev.username and ev.username.lower() in self.PRIVILEGED_USERS:
                # Direct remote login to privileged user from external or unexpected network
                is_external = True
                if ev.source_ip:
                    try:
                        ip_obj = ipaddress.ip_address(ev.source_ip)
                        is_external = not ip_obj.is_private and not ip_obj.is_loopback
                    except Exception:
                        pass

                if is_external:
                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=1,
                        is_critical_account=True,
                        is_external_ip=True
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"Direct External Remote Login as Privileged User '{ev.username}' from {ev.source_ip}",
                        "category": self.category,
                        "severity": "CRITICAL",
                        "source_ip": ev.source_ip,
                        "target_username": ev.username,
                        "timestamp": ev.timestamp,
                        "evidence": {
                            "account": ev.username,
                            "source_ip": ev.source_ip,
                            "service": ev.service or "ssh",
                            "hostname": ev.hostname,
                            "is_external": True,
                            "event_id": ev.event_uuid
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Verify if direct remote root/admin access violates security policy (PermitRootLogin no). Audit commands executed during session.",
                        "confidence_score": confidence
                    })

        return alerts
