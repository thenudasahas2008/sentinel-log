import abc
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.event import SecurityEvent

class BaseDetectionRule(abc.ABC):
    rule_id: str = "BASE_RULE"
    name: str = "Base Detection Rule"
    category: str = "GENERAL"
    severity: str = "MEDIUM"
    default_confidence: float = 0.80
    mitre_attack_id: str = "T1078"

    @abc.abstractmethod
    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Evaluates a slice of security events and returns a list of alert dictionaries if detected.
        Each alert dict must contain:
        - rule_id
        - title
        - category
        - severity
        - source_ip
        - target_username
        - timestamp
        - evidence (dict)
        - detection_rule_name
        - recommended_action
        - confidence_score
        """
        pass
