"""
IT Ticket Entity Class
Represents an IT support ticket
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict


@dataclass
class ITTicket:
    """IT ticket entity"""
    ticket_id: str
    assigned_staff: str
    priority: str  # "Critical", "High", "Medium", "Low"
    created_date: date
    status: str
    total_resolution_time_hours: float
    resolution_date: Optional[date] = None
    stage_times: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate ticket data"""
        if self.priority not in ["Critical", "High", "Medium", "Low"]:
            raise ValueError(f"Invalid priority: {self.priority}")
        if self.total_resolution_time_hours < 0:
            raise ValueError("Resolution time cannot be negative")
    
    def is_resolved(self) -> bool:
        """Check if ticket is resolved"""
        return self.status == "Resolved"
    
    def is_open(self) -> bool:
        """Check if ticket is open"""
        return self.status != "Resolved"
    
    def get_time_in_stage(self, stage: str) -> float:
        """Get time spent in a specific stage"""
        return self.stage_times.get(stage, 0.0)
    
    def get_bottleneck_stage(self) -> Optional[str]:
        """Get the stage with the longest time"""
        if not self.stage_times:
            return None
        return max(self.stage_times.items(), key=lambda x: x[1])[0]
    
    def to_dict(self) -> dict:
        """Convert ticket to dictionary"""
        result = {
            "Ticket ID": self.ticket_id,
            "Assigned Staff": self.assigned_staff,
            "Priority": self.priority,
            "Created Date": self.created_date,
            "Status": self.status,
            "Total Resolution Time (hours)": round(self.total_resolution_time_hours, 2),
            "Resolution Date": self.resolution_date
        }
        # Add stage times
        for stage, time in self.stage_times.items():
            result[f"Time in {stage} (hours)"] = round(time, 2)
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ITTicket':
        """Create ticket from dictionary"""
        # Extract stage times
        stage_times = {}
        for key, value in data.items():
            if key.startswith("Time in ") and key.endswith(" (hours)"):
                stage = key.replace("Time in ", "").replace(" (hours)", "")
                stage_times[stage] = value
        
        return cls(
            ticket_id=data["Ticket ID"],
            assigned_staff=data["Assigned Staff"],
            priority=data["Priority"],
            created_date=data["Created Date"],
            status=data["Status"],
            total_resolution_time_hours=data["Total Resolution Time (hours)"],
            resolution_date=data.get("Resolution Date"),
            stage_times=stage_times
        )

