"""
Security Incident Repository
Handles security incident data using database or in-memory storage
"""

import sys
import os
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path for app imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.data.db import connect_database
from app.data.incidents import get_all_incidents
from ..models.incident import SecurityIncident


class SecurityIncidentRepository:
    """Repository for security incident data"""
    
    def __init__(self, incidents: List[SecurityIncident] = None, use_database: bool = True):
        """
        Initialize repository
        
        Args:
            incidents: List of incidents (defaults to empty list or loads from DB)
            use_database: If True, load from database; if False, use provided incidents
        """
        if use_database:
            self._incidents = self._load_from_database()
        else:
            self._incidents = incidents if incidents is not None else []
    
    def _load_from_database(self) -> List[SecurityIncident]:
        """Load incidents from database"""
        try:
            df = get_all_incidents()
            if df.empty:
                return []
            
            incidents = []
            for _, row in df.iterrows():
                # Map database columns to model
                # Database: date, incident_type, severity, status, description, reported_by
                # Model: date, threat_category, severity, status, resolution_time_hours
                try:
                    date = pd.to_datetime(row['date']).to_pydatetime()
                    
                    # Map severity: Critical -> High (model only accepts High/Medium/Low)
                    severity = row.get('severity', 'Medium')
                    if severity == 'Critical':
                        severity = 'High'
                    
                    # Get status and handle resolved incidents
                    status = row.get('status', 'Unresolved')
                    resolution_time_hours = None
                    
                    # If status is Resolved but no resolution time, set a default or change status
                    if status == 'Resolved':
                        # Set a default resolution time (24 hours) if not available
                        resolution_time_hours = 24.0
                    
                    incident = SecurityIncident(
                        date=date,
                        threat_category=row.get('incident_type', 'Unknown'),
                        severity=severity,
                        status=status,
                        resolution_time_hours=resolution_time_hours
                    )
                    incidents.append(incident)
                except Exception as e:
                    print(f"Error loading incident {row.get('id', 'unknown')}: {e}")
                    continue
            return incidents
        except Exception as e:
            print(f"Error loading incidents from database: {e}")
            return []
    
    def add(self, incident: SecurityIncident) -> None:
        """Add an incident to the repository"""
        self._incidents.append(incident)
    
    def add_all(self, incidents: List[SecurityIncident]) -> None:
        """Add multiple incidents"""
        self._incidents.extend(incidents)
    
    def get_all(self) -> List[SecurityIncident]:
        """Get all incidents"""
        return self._incidents.copy()
    
    def get_by_category(self, category: str) -> List[SecurityIncident]:
        """Get incidents by threat category"""
        return [inc for inc in self._incidents if inc.threat_category == category]
    
    def get_by_status(self, status: str) -> List[SecurityIncident]:
        """Get incidents by status"""
        return [inc for inc in self._incidents if inc.status == status]
    
    def get_unresolved_high_severity(self) -> List[SecurityIncident]:
        """Get unresolved high-severity incidents"""
        return [inc for inc in self._incidents if inc.is_unresolved() and inc.is_high_severity()]
    
    def get_resolved(self) -> List[SecurityIncident]:
        """Get all resolved incidents"""
        return [inc for inc in self._incidents if inc.status == "Resolved"]
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert incidents to pandas DataFrame"""
        if not self._incidents:
            return pd.DataFrame()
        return pd.DataFrame([inc.to_dict() for inc in self._incidents])
    
    def count(self) -> int:
        """Get total count of incidents"""
        return len(self._incidents)

