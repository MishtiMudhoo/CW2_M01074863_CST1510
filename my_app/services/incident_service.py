"""
Security Incident Service
Business logic for security incidents
"""

from typing import List, Dict, Optional
import pandas as pd
from ..models.incident import SecurityIncident
from ..repositories.incident_repository import SecurityIncidentRepository


class SecurityIncidentService:
    """Service for security incident business logic"""
    
    def __init__(self, repository: SecurityIncidentRepository):
        """
        Initialize service
        
        Args:
            repository: Security incident repository instance
        """
        self.repository = repository
    
    def get_metrics(self) -> Dict:
        """Get key metrics for incidents"""
        all_incidents = self.repository.get_all()
        unresolved_high = self.repository.get_unresolved_high_severity()
        phishing_incidents = self.repository.get_by_category("Phishing")
        phishing_unresolved = [inc for inc in phishing_incidents if inc.is_unresolved()]
        
        return {
            "total_incidents": len(all_incidents),
            "unresolved_high": len(unresolved_high),
            "phishing_total": len(phishing_incidents),
            "phishing_unresolved": len(phishing_unresolved)
        }
    
    def get_phishing_surge_analysis(self, days: int = 7) -> Dict:
        """
        Analyze phishing surge
        
        Args:
            days: Number of recent days to analyze
            
        Returns:
            Dictionary with surge analysis
        """
        from datetime import datetime, timedelta
        all_incidents = self.repository.get_all()
        end_date = datetime.now()
        recent_date = end_date - timedelta(days=days)
        previous_date = end_date - timedelta(days=days*2)
        
        recent_phishing = [
            inc for inc in all_incidents 
            if inc.threat_category == "Phishing" and inc.date >= recent_date
        ]
        previous_phishing = [
            inc for inc in all_incidents 
            if inc.threat_category == "Phishing" and previous_date <= inc.date < recent_date
        ]
        
        recent_count = len(recent_phishing)
        previous_count = len(previous_phishing)
        surge_percentage = ((recent_count - previous_count) / max(previous_count, 1)) * 100
        
        return {
            "recent_count": recent_count,
            "previous_count": previous_count,
            "surge_percentage": surge_percentage
        }
    
    def get_resolution_bottleneck(self) -> Optional[Dict]:
        """
        Identify the threat category with longest resolution time
        
        Returns:
            Dictionary with bottleneck information or None
        """
        resolved = self.repository.get_resolved()
        if not resolved:
            return None
        
        # Group by category and calculate average
        category_times = {}
        for incident in resolved:
            if incident.resolution_time_hours:
                if incident.threat_category not in category_times:
                    category_times[incident.threat_category] = []
                category_times[incident.threat_category].append(incident.resolution_time_hours)
        
        if not category_times:
            return None
        
        # Calculate averages
        avg_times = {
            cat: sum(times) / len(times) 
            for cat, times in category_times.items()
        }
        
        # Find longest
        longest_category = max(avg_times.items(), key=lambda x: x[1])
        
        return {
            "category": longest_category[0],
            "avg_resolution_time": longest_category[1],
            "all_averages": avg_times
        }
    
    def get_backlog_summary(self) -> Dict:
        """Get backlog summary"""
        unresolved = self.repository.get_by_status("Unresolved")
        high_severity_unresolved = self.repository.get_unresolved_high_severity()
        
        # Group by category
        by_category = {}
        for incident in unresolved:
            if incident.threat_category not in by_category:
                by_category[incident.threat_category] = 0
            by_category[incident.threat_category] += 1
        
        return {
            "total_unresolved": len(unresolved),
            "high_severity_unresolved": len(high_severity_unresolved),
            "by_category": by_category
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert incidents to DataFrame"""
        return self.repository.to_dataframe()

