from dataclasses import dataclass
from typing import Optional

@dataclass
class Finding:
    id: str
    severity: str  # High, Medium, Low
    resource: str
    resource_id: str
    region: str
    annual_recovery: float
    classification: str
    description: str
    cli_remediation: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "severity": self.severity,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "region": self.region,
            "annual_recovery": self.annual_recovery,
            "classification": self.classification,
            "description": self.description,
            "cli_remediation": self.cli_remediation
        }