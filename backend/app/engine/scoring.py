import math
from typing import Dict, Any

class ConfidenceScorer:
    """
    Computes a deterministic, documented confidence score (0.0 to 1.0)
    for security detection alerts based on:
    - Evidence quantity & velocity (frequency factor)
    - Target criticality (e.g., root/admin accounts)
    - IP reputation & type (external vs internal RFC 1918)
    - Temporal context (off-hours multiplier)
    """

    CRITICAL_ACCOUNTS = {"root", "administrator", "admin", "system", "postgres", "sa", "oracle", "dbadmin"}

    @classmethod
    def calculate_confidence(
        cls,
        base_rule_confidence: float,
        failure_count: int,
        distinct_users: int = 1,
        is_critical_account: bool = False,
        is_external_ip: bool = True,
        is_off_hours: bool = False,
        velocity_per_minute: float = 1.0
    ) -> float:
        score = base_rule_confidence

        # 1. Volume Factor: More attempts increase confidence non-linearly
        if failure_count >= 20:
            score += 0.12
        elif failure_count >= 10:
            score += 0.08
        elif failure_count >= 5:
            score += 0.04

        # 2. Velocity Factor: Rapid fire attempts indicate automation/bot
        if velocity_per_minute >= 10.0:
            score += 0.08
        elif velocity_per_minute >= 3.0:
            score += 0.04

        # 3. Target Criticality: Attacking high-value accounts adds weight
        if is_critical_account:
            score += 0.06

        # 4. External IP: External untrusted origins are more suspicious
        if is_external_ip:
            score += 0.05
        else:
            score -= 0.05  # Internal LAN can be benign misconfig

        # 5. Off-Hours Multiplier
        if is_off_hours:
            score += 0.04

        # 6. Breadth Factor: Spraying multiple users
        if distinct_users >= 5:
            score += 0.08
        elif distinct_users >= 3:
            score += 0.04

        # Bound between 0.30 and 0.99 (never absolute 1.00 in probabilistic detection)
        final_score = max(0.30, min(0.99, score))
        return round(final_score, 2)
