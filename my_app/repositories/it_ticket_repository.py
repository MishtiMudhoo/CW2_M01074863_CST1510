"""
IT Ticket Repository
Handles IT ticket data using database or in-memory storage
"""

import sys
import os
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd

# Add parent directory to path for app imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.data.db import connect_database
from ..models.it_ticket import ITTicket


class ITTicketRepository:
    """Repository for IT ticket data"""
    
    def __init__(self, tickets: List[ITTicket] = None, use_database: bool = True):
        """
        Initialize repository
        
        Args:
            tickets: List of tickets (defaults to empty list or loads from DB)
            use_database: If True, load from database; if False, use provided tickets
        """
        if use_database:
            self._tickets = self._load_from_database()
        else:
            self._tickets = tickets if tickets is not None else []
    
    def _load_from_database(self) -> List[ITTicket]:
        """Load tickets from database"""
        try:
            conn = connect_database()
            df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
            conn.close()
            
            if df.empty:
                return []
            
            tickets = []
            for _, row in df.iterrows():
                # Map database columns to model
                # Database: ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to
                # Model: ticket_id, assigned_staff, priority, created_date, status, total_resolution_time_hours, resolution_date, stage_times
                try:
                    created_date = pd.to_datetime(row.get('created_date', datetime.now())).date()
                    resolution_date = None
                    if pd.notna(row.get('resolved_date')):
                        resolution_date = pd.to_datetime(row['resolved_date']).date()
                    
                    # Calculate resolution time if resolved
                    total_time = 0.0
                    if resolution_date:
                        delta = resolution_date - created_date
                        total_time = delta.total_seconds() / 3600  # Convert to hours
                    
                    # Create default stage times (not in DB schema)
                    stage_times: Dict[str, float] = {}
                    if total_time > 0:
                        # Distribute time across stages (simplified)
                        stage_times = {
                            "New": total_time * 0.1,
                            "Assigned": total_time * 0.1,
                            "In Progress": total_time * 0.3,
                            "Waiting for User": total_time * 0.3,
                            "Resolved": total_time * 0.2
                        }
                    
                    ticket = ITTicket(
                        ticket_id=row.get('ticket_id', f"TKT-{row.get('id', '0000')}"),
                        assigned_staff=row.get('assigned_to', 'Unassigned'),
                        priority=row.get('priority', 'Medium'),
                        created_date=created_date,
                        status=row.get('status', 'New'),
                        total_resolution_time_hours=round(total_time, 2),
                        resolution_date=resolution_date,
                        stage_times=stage_times
                    )
                    tickets.append(ticket)
                except Exception as e:
                    print(f"Error loading ticket {row.get('id', 'unknown')}: {e}")
                    continue
            return tickets
        except Exception as e:
            print(f"Error loading tickets from database: {e}")
            return []
    
    def add(self, ticket: ITTicket) -> None:
        """Add a ticket to the repository"""
        self._tickets.append(ticket)
    
    def add_all(self, tickets: List[ITTicket]) -> None:
        """Add multiple tickets"""
        self._tickets.extend(tickets)
    
    def get_all(self) -> List[ITTicket]:
        """Get all tickets"""
        return self._tickets.copy()
    
    def get_by_staff(self, staff_name: str) -> List[ITTicket]:
        """Get tickets assigned to a staff member"""
        return [ticket for ticket in self._tickets if ticket.assigned_staff == staff_name]
    
    def get_by_status(self, status: str) -> List[ITTicket]:
        """Get tickets by status"""
        return [ticket for ticket in self._tickets if ticket.status == status]
    
    def get_by_priority(self, priority: str) -> List[ITTicket]:
        """Get tickets by priority"""
        return [ticket for ticket in self._tickets if ticket.priority == priority]
    
    def get_resolved(self) -> List[ITTicket]:
        """Get all resolved tickets"""
        return [ticket for ticket in self._tickets if ticket.is_resolved()]
    
    def get_open(self) -> List[ITTicket]:
        """Get all open tickets"""
        return [ticket for ticket in self._tickets if ticket.is_open()]
    
    def get_waiting_for_user(self) -> List[ITTicket]:
        """Get tickets waiting for user"""
        return [ticket for ticket in self._tickets if ticket.status == "Waiting for User"]
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert tickets to pandas DataFrame"""
        if not self._tickets:
            return pd.DataFrame()
        return pd.DataFrame([ticket.to_dict() for ticket in self._tickets])
    
    def count(self) -> int:
        """Get total count of tickets"""
        return len(self._tickets)

