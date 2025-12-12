"""
Data Generators
Generate sample data for entities
Can also load from database if available
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.incident import SecurityIncident
from ..models.dataset import Dataset
from ..models.it_ticket import ITTicket


class SecurityIncidentGenerator:
    """Generator for security incident data"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize generator
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
    
    def generate(self, days: int = 30) -> List[SecurityIncident]:
        """
        Generate security incidents for specified days
        
        Args:
            days: Number of days to generate data for
            
        Returns:
            List of SecurityIncident objects
        """
        incidents = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = [start_date + timedelta(days=i) for i in range(days)]
        
        threat_categories = ["Phishing", "Malware", "DDoS", "Unauthorized Access", "Data Breach", "Ransomware"]
        
        for date in dates:
            base_phishing = 2
            base_others = np.random.randint(1, 4)
            days_ago = (end_date - date).days
            phishing_multiplier = max(1, 3 - (days_ago / 10))
            phishing_count = int(base_phishing * phishing_multiplier + np.random.randint(0, 5))
            
            # Generate phishing incidents
            for _ in range(phishing_count):
                severity = np.random.choice(["High", "Medium", "Low"], p=[0.6, 0.3, 0.1])
                status = np.random.choice(["Unresolved", "In Progress", "Resolved"], p=[0.5, 0.3, 0.2])
                resolution_time = np.random.randint(2, 72) if status == "Resolved" else None
                
                incidents.append(SecurityIncident(
                    date=date,
                    threat_category="Phishing",
                    severity=severity,
                    status=status,
                    resolution_time_hours=resolution_time
                ))
            
            # Generate other threat categories
            for category in threat_categories[1:]:
                count = np.random.randint(0, base_others)
                for _ in range(count):
                    severity = np.random.choice(["High", "Medium", "Low"], p=[0.4, 0.4, 0.2])
                    status = np.random.choice(["Unresolved", "In Progress", "Resolved"], p=[0.3, 0.3, 0.4])
                    resolution_time = np.random.randint(1, 48) if status == "Resolved" else None
                    
                    incidents.append(SecurityIncident(
                        date=date,
                        threat_category=category,
                        severity=severity,
                        status=status,
                        resolution_time_hours=resolution_time
                    ))
        
        return incidents


class DatasetGenerator:
    """Generator for dataset catalog data"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize generator
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
    
    def generate(self) -> List[Dataset]:
        """
        Generate dataset catalog data
        
        Returns:
            List of Dataset objects
        """
        datasets = []
        departments = ["IT", "Cyber", "IT", "Cyber", "IT", "Cyber", "IT", "Finance", "HR", "IT", "Cyber", "IT"]
        dataset_names = [
            "Network_Logs_2024", "Security_Incidents_Q1", "Server_Metrics_Daily", 
            "Phishing_Attempts_Log", "Database_Backup_Metadata", "Firewall_Rules_Export",
            "Application_Logs_Production", "User_Access_Logs", "Employee_Data_Export",
            "System_Performance_Metrics", "Threat_Intelligence_Feed", "Infrastructure_Monitoring"
        ]
        
        for dept, name in zip(departments, dataset_names):
            if dept in ["IT", "Cyber"]:
                size_gb = np.random.uniform(50, 500)
            else:
                size_gb = np.random.uniform(5, 50)
            
            rows_millions = size_gb * np.random.uniform(0.5, 2.0)
            days_ago = np.random.randint(1, 180)
            upload_date = datetime.now() - timedelta(days=days_ago)
            last_accessed_days = np.random.randint(0, days_ago)
            last_accessed = datetime.now() - timedelta(days=last_accessed_days) if last_accessed_days < days_ago else upload_date
            quality_status = np.random.choice(["Passed", "Failed", "Pending"], p=[0.6, 0.2, 0.2])
            dependencies = np.random.randint(0, 5)
            access_frequency = np.random.randint(0, 50)
            
            dataset = Dataset(
                name=name,
                department=dept,
                size_gb=round(size_gb, 2),
                rows_millions=round(rows_millions, 2),
                upload_date=upload_date.date(),
                last_accessed=last_accessed.date(),
                days_since_access=(datetime.now() - last_accessed).days,
                quality_status=quality_status,
                dependencies=dependencies,
                access_frequency_30d=access_frequency,
                storage_cost_per_month=round(size_gb * 0.023, 2)
            )
            
            # Calculate archive score
            dataset.calculate_archive_score()
            datasets.append(dataset)
        
        return datasets


class ITTicketGenerator:
    """Generator for IT ticket data"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize generator
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
    
    def generate(self, num_tickets: int = 150) -> List[ITTicket]:
        """
        Generate IT ticket data
        
        Args:
            num_tickets: Number of tickets to generate
            
        Returns:
            List of ITTicket objects
        """
        tickets = []
        staff_members = ["John Smith", "Sarah Johnson", "Mike Davis", "Emily Chen", "David Wilson", "Lisa Anderson"]
        process_stages = ["New", "Assigned", "In Progress", "Waiting for User", "Waiting for Vendor", "Escalated", "Resolved"]
        
        for ticket_id in range(1, num_tickets + 1):
            assigned_staff = np.random.choice(staff_members)
            
            # Create performance anomaly for one staff member
            if assigned_staff == "John Smith":
                base_delay_multiplier = np.random.uniform(1.5, 2.5)
            else:
                base_delay_multiplier = np.random.uniform(0.8, 1.2)
            
            priority = np.random.choice(["Critical", "High", "Medium", "Low"], p=[0.1, 0.2, 0.5, 0.2])
            days_ago = np.random.randint(1, 60)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            # Time spent in each stage
            stage_times = {}
            total_time = 0
            
            for stage in process_stages:
                if stage == "New":
                    time_spent = np.random.uniform(0.5, 2) * base_delay_multiplier
                elif stage == "Assigned":
                    time_spent = np.random.uniform(1, 4) * base_delay_multiplier
                elif stage == "In Progress":
                    time_spent = np.random.uniform(2, 8) * base_delay_multiplier
                elif stage == "Waiting for User":
                    if np.random.random() < 0.4:
                        time_spent = np.random.uniform(12, 48) * base_delay_multiplier
                    else:
                        time_spent = np.random.uniform(2, 8) * base_delay_multiplier
                elif stage == "Waiting for Vendor":
                    if np.random.random() < 0.2:
                        time_spent = np.random.uniform(24, 72) * base_delay_multiplier
                    else:
                        time_spent = np.random.uniform(4, 12) * base_delay_multiplier
                elif stage == "Escalated":
                    time_spent = np.random.uniform(4, 16) * base_delay_multiplier
                else:  # Resolved
                    time_spent = np.random.uniform(1, 4) * base_delay_multiplier
                
                stage_times[stage] = round(time_spent, 2)
                total_time += time_spent
            
            # Status
            if days_ago < 3:
                status = np.random.choice(["In Progress", "Waiting for User", "Waiting for Vendor"], p=[0.4, 0.4, 0.2])
            else:
                status = "Resolved"
            
            # Resolution date
            resolution_date = None
            if status == "Resolved":
                resolution_date = (created_date + timedelta(hours=total_time)).date()
            
            ticket = ITTicket(
                ticket_id=f"TKT-{ticket_id:04d}",
                assigned_staff=assigned_staff,
                priority=priority,
                created_date=created_date.date(),
                status=status,
                total_resolution_time_hours=round(total_time, 2),
                resolution_date=resolution_date,
                stage_times=stage_times
            )
            
            tickets.append(ticket)
        
        return tickets

