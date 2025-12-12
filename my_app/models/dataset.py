"""
Dataset Entity Class
Represents a dataset in the catalog
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class Dataset:
    """Dataset entity representing a data catalog entry"""
    name: str
    department: str
    size_gb: float
    rows_millions: float
    upload_date: date
    last_accessed: date
    days_since_access: int
    quality_status: str  # "Passed", "Failed", "Pending"
    dependencies: int
    access_frequency_30d: int
    storage_cost_per_month: float
    archive_score: Optional[float] = None
    
    def __post_init__(self):
        """Validate dataset data"""
        if self.quality_status not in ["Passed", "Failed", "Pending"]:
            raise ValueError(f"Invalid quality status: {self.quality_status}")
        if self.size_gb < 0:
            raise ValueError("Size cannot be negative")
    
    def is_stale(self, days_threshold: int = 90) -> bool:
        """Check if dataset is stale (not accessed in threshold days)"""
        return self.days_since_access > days_threshold
    
    def is_rarely_accessed(self, threshold: int = 5) -> bool:
        """Check if dataset is rarely accessed"""
        return self.access_frequency_30d < threshold
    
    def calculate_archive_score(self) -> float:
        """
        Calculate archive score based on multiple factors
        Higher score = better candidate for archiving
        """
        score = (
            (self.days_since_access / 180) * 0.4 +  # Older = higher score
            (1 - self.access_frequency_30d / 50) * 0.3 +  # Less accessed = higher score
            (1 - self.dependencies / 5) * 0.2 +  # Fewer dependencies = higher score
            (self.size_gb / 500) * 0.1  # Larger size = higher score (but less weight)
        ) * 100
        self.archive_score = score
        return score
    
    def to_dict(self) -> dict:
        """Convert dataset to dictionary"""
        return {
            "Dataset Name": self.name,
            "Department": self.department,
            "Size (GB)": round(self.size_gb, 2),
            "Rows (Millions)": round(self.rows_millions, 2),
            "Upload Date": self.upload_date,
            "Last Accessed": self.last_accessed,
            "Days Since Access": self.days_since_access,
            "Quality Status": self.quality_status,
            "Dependencies": self.dependencies,
            "Access Frequency (30d)": self.access_frequency_30d,
            "Storage Cost ($/month)": round(self.storage_cost_per_month, 2),
            "Archive Score": round(self.archive_score, 2) if self.archive_score else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Dataset':
        """Create dataset from dictionary"""
        return cls(
            name=data["Dataset Name"],
            department=data["Department"],
            size_gb=data["Size (GB)"],
            rows_millions=data["Rows (Millions)"],
            upload_date=data["Upload Date"],
            last_accessed=data["Last Accessed"],
            days_since_access=data["Days Since Access"],
            quality_status=data["Quality Status"],
            dependencies=data["Dependencies"],
            access_frequency_30d=data["Access Frequency (30d)"],
            storage_cost_per_month=data["Storage Cost ($/month)"],
            archive_score=data.get("Archive Score")
        )

