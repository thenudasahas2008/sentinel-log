from typing import List, Type
from app.engine.rules.base import BaseDetectionRule
from app.engine.rules.brute_force import SSHBruteForceRule
from app.engine.rules.password_spray import PasswordSprayingRule
from app.engine.rules.credential_stuffing import CredentialStuffingRule
from app.engine.rules.repeated_failures import RepeatedFailuresRule
from app.engine.rules.login_after_failures import LoginAfterFailuresRule
from app.engine.rules.suspicious_hours import SuspiciousHoursRule
from app.engine.rules.multi_source_ip import MultiSourceIPRule
from app.engine.rules.impossible_travel import ImpossibleTravelRule
from app.engine.rules.privileged_anomaly import PrivilegedAccountAnomalyRule
from app.engine.rules.abnormal_spike import AbnormalFailureSpikeRule

ALL_RULES: List[Type[BaseDetectionRule]] = [
    SSHBruteForceRule,
    PasswordSprayingRule,
    CredentialStuffingRule,
    RepeatedFailuresRule,
    LoginAfterFailuresRule,
    SuspiciousHoursRule,
    MultiSourceIPRule,
    ImpossibleTravelRule,
    PrivilegedAccountAnomalyRule,
    AbnormalFailureSpikeRule
]

__all__ = [
    "BaseDetectionRule",
    "SSHBruteForceRule",
    "PasswordSprayingRule",
    "CredentialStuffingRule",
    "RepeatedFailuresRule",
    "LoginAfterFailuresRule",
    "SuspiciousHoursRule",
    "MultiSourceIPRule",
    "ImpossibleTravelRule",
    "PrivilegedAccountAnomalyRule",
    "AbnormalFailureSpikeRule",
    "ALL_RULES"
]
