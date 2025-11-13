from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    status: ValidationStatus
    severity: Severity
    rule_name: str
    message: str
