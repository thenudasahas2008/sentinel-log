import math
from datetime import timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional
from app.engine.rules.base import BaseDetectionRule
from app.engine.scoring import ConfidenceScorer
from app.models.event import SecurityEvent

class ImpossibleTravelRule(BaseDetectionRule):
    rule_id: str = "RULE-008"
    name: str = "Impossible Travel Velocity Indicator"
    category: str = "GEO_VELOCITY"
    severity: str = "CRITICAL"
    default_confidence: float = 0.94
    mitre_attack_id: str = "T1078.004"

    MAX_COMMERCIAL_SPEED_KMH: float = 900.0  # Speed of passenger airliner

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance in kilometers between two points."""
        r = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    def evaluate(self, events: List[SecurityEvent], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        alerts = []
        user_logins = defaultdict(list)

        for ev in events:
            # Check for metadata geo info or external context geo
            geo = None
            if ev.metadata_json and isinstance(ev.metadata_json, dict) and "geo" in ev.metadata_json:
                geo = ev.metadata_json["geo"]
            elif context and "ip_geo_map" in context and ev.source_ip:
                geo = context["ip_geo_map"].get(ev.source_ip)

            if ev.status == "SUCCESS" and ev.username and geo and "lat" in geo and "lon" in geo:
                user_logins[ev.username].append((ev, geo))

        for user, items in user_logins.items():
            items.sort(key=lambda x: x[0].timestamp)
            for i in range(len(items) - 1):
                ev1, geo1 = items[i]
                ev2, geo2 = items[i+1]

                delta_hours = (ev2.timestamp - ev1.timestamp).total_seconds() / 3600.0
                if delta_hours <= 0.01:
                    delta_hours = 0.01  # Prevent div zero

                distance_km = self.haversine_distance(
                    geo1["lat"], geo1["lon"],
                    geo2["lat"], geo2["lon"]
                )

                speed_kmh = distance_km / delta_hours

                # Only trigger if distance is significant (> 300 km) and speed exceeds air travel
                if distance_km > 300.0 and speed_kmh > self.MAX_COMMERCIAL_SPEED_KMH:
                    confidence = ConfidenceScorer.calculate_confidence(
                        base_rule_confidence=self.default_confidence,
                        failure_count=1,
                        is_critical_account=user.lower() in ConfidenceScorer.CRITICAL_ACCOUNTS
                    )

                    alerts.append({
                        "rule_id": self.rule_id,
                        "title": f"Impossible Travel for '{user}': {round(distance_km)}km in {round(delta_hours*60, 1)}m ({round(speed_kmh)} km/h)",
                        "category": self.category,
                        "severity": self.severity,
                        "source_ip": ev2.source_ip,
                        "target_username": user,
                        "timestamp": ev2.timestamp,
                        "evidence": {
                            "origin_ip": ev1.source_ip,
                            "origin_location": geo1.get("city", "Location A"),
                            "origin_time": ev1.timestamp.isoformat(),
                            "dest_ip": ev2.source_ip,
                            "dest_location": geo2.get("city", "Location B"),
                            "dest_time": ev2.timestamp.isoformat(),
                            "distance_km": round(distance_km, 2),
                            "travel_duration_hours": round(delta_hours, 2),
                            "required_velocity_kmh": round(speed_kmh, 2),
                            "event_1": ev1.event_uuid,
                            "event_2": ev2.event_uuid
                        },
                        "detection_rule_name": self.name,
                        "recommended_action": f"Revoke current sessions for '{user}', require immediate step-up authentication, verify VPN / proxy egress status.",
                        "confidence_score": confidence
                    })

        return alerts
