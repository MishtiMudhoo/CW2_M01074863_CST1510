"""
IT Ticket Service
Business logic for IT tickets
"""

from typing import List, Dict, Optional
import pandas as pd
from ..models.it_ticket import ITTicket
from ..repositories.it_ticket_repository import ITTicketRepository


class ITTicketService:
    """Service for IT ticket business logic"""
    
    def __init__(self, repository: ITTicketRepository):
        """
        Initialize service
        
        Args:
            repository: IT ticket repository instance
        """
        self.repository = repository
    
    def get_metrics(self) -> Dict:
        """Get key metrics for tickets"""
        all_tickets = self.repository.get_all()
        open_tickets = self.repository.get_open()
        resolved = self.repository.get_resolved()
        waiting_user = self.repository.get_waiting_for_user()
        
        avg_resolution = 0
        if resolved:
            avg_resolution = sum(
                t.total_resolution_time_hours for t in resolved
            ) / len(resolved)
        
        return {
            "total_tickets": len(all_tickets),
            "open_tickets": len(open_tickets),
            "avg_resolution_time": avg_resolution,
            "tickets_waiting_user": len(waiting_user)
        }
    
    def get_staff_performance(self) -> Dict:
        """
        Analyze staff performance
        
        Returns:
            Dictionary with staff performance metrics
        """
        resolved = self.repository.get_resolved()
        if not resolved:
            return {"staff_performance": {}, "slowest_staff": None}
        
        # Group by staff
        staff_times = {}
        for ticket in resolved:
            if ticket.assigned_staff not in staff_times:
                staff_times[ticket.assigned_staff] = []
            staff_times[ticket.assigned_staff].append(ticket.total_resolution_time_hours)
        
        # Calculate averages
        staff_avg = {
            staff: sum(times) / len(times)
            for staff, times in staff_times.items()
        }
        
        # Find slowest
        slowest_staff = max(staff_avg.items(), key=lambda x: x[1]) if staff_avg else None
        
        # Calculate team average
        team_avg = sum(staff_avg.values()) / len(staff_avg) if staff_avg else 0
        
        # Calculate performance gap
        performance_gap = None
        if slowest_staff:
            gap = slowest_staff[1] - team_avg
            gap_pct = (gap / team_avg * 100) if team_avg > 0 else 0
            performance_gap = {
                "staff": slowest_staff[0],
                "avg_time": slowest_staff[1],
                "team_avg": team_avg,
                "gap_hours": gap,
                "gap_percentage": gap_pct
            }
        
        return {
            "staff_performance": staff_avg,
            "slowest_staff": performance_gap,
            "team_average": team_avg
        }
    
    def get_process_bottleneck(self) -> Optional[Dict]:
        """
        Identify the process stage causing the greatest delay
        
        Returns:
            Dictionary with bottleneck information or None
        """
        all_tickets = self.repository.get_all()
        if not all_tickets:
            return None
        
        # Collect all stage times
        stage_totals = {}
        stage_counts = {}
        
        for ticket in all_tickets:
            for stage, time in ticket.stage_times.items():
                if stage not in stage_totals:
                    stage_totals[stage] = 0
                    stage_counts[stage] = 0
                stage_totals[stage] += time
                stage_counts[stage] += 1
        
        if not stage_totals:
            return None
        
        # Calculate averages
        stage_averages = {
            stage: stage_totals[stage] / stage_counts[stage]
            for stage in stage_totals
        }
        
        # Find bottleneck
        bottleneck_stage = max(stage_averages.items(), key=lambda x: x[1])
        
        # Calculate percentage of total time
        total_time = sum(stage_totals.values())
        percentage = (stage_totals[bottleneck_stage[0]] / total_time * 100) if total_time > 0 else 0
        
        return {
            "stage": bottleneck_stage[0],
            "avg_time": bottleneck_stage[1],
            "total_time": stage_totals[bottleneck_stage[0]],
            "percentage": percentage,
            "all_stages": stage_averages
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert tickets to DataFrame"""
        return self.repository.to_dataframe()

