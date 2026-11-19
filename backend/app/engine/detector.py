import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.event import SecurityEvent
from app.models.alert import Alert
from app.engine.rules import ALL_RULES, BaseDetectionRule
from app.utils.logging import logger

class DetectionEngine:
    def __init__(self, rules: Optional[List[BaseDetectionRule]] = None):
        self.rules: List[BaseDetectionRule] = rules if rules is not None else [rule_cls() for rule_cls in ALL_RULES]

    def analyze_events(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Runs all registered detection rules against the given events.
        Returns a list of generated alert dictionaries.
        """
        detected_alerts = []
        if not events:
            return detected_alerts

        for rule in self.rules:
            try:
                rule_alerts = rule.evaluate(events, context=context)
                if rule_alerts:
                    logger.info(f"Rule [{rule.rule_id}] {rule.name} triggered {len(rule_alerts)} alert(s)")
                    detected_alerts.extend(rule_alerts)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {str(e)}", exc_info=True)

        return detected_alerts

    def process_and_persist(self, db: Session, events: List[SecurityEvent], is_synthetic: bool = False) -> List[Alert]:
        """
        Runs detection engine on events, creates Alert database objects, and commits them.
        """
        raw_alerts = self.analyze_events(events)
        created_alerts = []

        for item in raw_alerts:
            # Check for recent duplicate alert from same rule and same IP / user within 1 hour
            alert_obj = Alert(
                alert_uuid=f"alt-{uuid.uuid4().hex[:16]}",
                rule_id=item["rule_id"],
                title=item["title"],
                category=item["category"],
                severity=item["severity"],
                source_ip=item.get("source_ip"),
                target_username=item.get("target_username"),
                timestamp=item["timestamp"],
                evidence=item["evidence"],
                detection_rule_name=item["detection_rule_name"],
                recommended_action=item["recommended_action"],
                confidence_score=item["confidence_score"],
                status="NEW",
                is_synthetic=is_synthetic
            )
            db.add(alert_obj)
            created_alerts.append(alert_obj)

        if created_alerts:
            db.commit()
            for a in created_alerts:
                db.refresh(a)

        return created_alerts
