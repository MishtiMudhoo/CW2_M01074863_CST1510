"""
Security Incident Entity Class
Represents a security incident
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SecurityIncident:
    """Security incident entity"""
    date: datetime
    threat_category: str
    severity: str  # "High", "Medium", "Low"
    status: str  # "Unresolved", "In Progress", "Resolved"
    resolution_time_hours: Optional[float] = None
    
    def __post_init__(self):
        """Validate incident data"""
        if self.severity not in ["High", "Medium", "Low"]:
            raise ValueError(f"Invalid severity: {self.severity}")
        if self.status not in ["Unresolved", "In Progress", "Resolved"]:
            raise ValueError(f"Invalid status: {self.status}")
        if self.status == "Resolved" and self.resolution_time_hours is None:
            raise ValueError("Resolved incidents must have resolution time")
    
    def is_unresolved(self) -> bool:
        """Check if incident is unresolved"""
        return self.status == "Unresolved"
    
    def is_high_severity(self) -> bool:
        """Check if incident is high severity"""
        return self.severity == "High"
    
    def to_dict(self) -> dict:
        """Convert incident to dictionary"""
        return {
            "Date": self.date,
            "Threat Category": self.threat_category,
            "Severity": self.severity,
            "Status": self.status,
            "Resolution Time (hours)": self.resolution_time_hours
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SecurityIncident':
        """Create incident from dictionary"""
        return cls(
            date=data["Date"],
            threat_category=data["Threat Category"],
            severity=data["Severity"],
            status=data["Status"],
            resolution_time_hours=data.get("Resolution Time (hours)")
        )

