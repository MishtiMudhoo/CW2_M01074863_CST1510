"""
Dataset Service
Business logic for dataset management
"""

from typing import List, Dict
import pandas as pd
from ..models.dataset import Dataset
from ..repositories.dataset_repository import DatasetRepository


class DatasetService:
    """Service for dataset business logic"""
    
    def __init__(self, repository: DatasetRepository):
        """
        Initialize service
        
        Args:
            repository: Dataset repository instance
        """
        self.repository = repository
    
    def get_metrics(self) -> Dict:
        """Get key metrics for datasets"""
        all_datasets = self.repository.get_all()
        pending_quality = self.repository.get_by_quality_status("Pending")
        
        return {
            "total_datasets": len(all_datasets),
            "total_storage_gb": self.repository.get_total_storage(),
            "total_storage_cost": self.repository.get_total_cost(),
            "pending_quality_checks": len(pending_quality)
        }
    
    def get_resource_consumption_by_department(self) -> Dict:
        """Get resource consumption breakdown by department"""
        all_datasets = self.repository.get_all()
        
        dept_size = {}
        dept_rows = {}
        
        for dataset in all_datasets:
            if dataset.department not in dept_size:
                dept_size[dataset.department] = 0
                dept_rows[dataset.department] = 0
            dept_size[dataset.department] += dataset.size_gb
            dept_rows[dataset.department] += dataset.rows_millions
        
        return {
            "size_by_department": dept_size,
            "rows_by_department": dept_rows
        }
    
    def get_dependency_analysis(self) -> Dict:
        """Analyze dataset dependencies"""
        all_datasets = self.repository.get_all()
        
        high_dependency = sorted(
            all_datasets, 
            key=lambda x: x.dependencies, 
            reverse=True
        )[:5]
        
        # Risk assessment
        risk_levels = {"High": 0, "Medium": 0, "Low": 0}
        for dataset in all_datasets:
            if dataset.dependencies >= 3:
                risk_levels["High"] += 1
            elif dataset.dependencies >= 1:
                risk_levels["Medium"] += 1
            else:
                risk_levels["Low"] += 1
        
        return {
            "high_dependency_datasets": high_dependency,
            "risk_levels": risk_levels
        }
    
    def get_archiving_recommendations(self, limit: int = 5) -> Dict:
        """Get archiving recommendations"""
        candidates = self.repository.get_archive_candidates(limit)
        
        if not candidates:
            return {
                "candidates": [],
                "potential_savings_gb": 0,
                "potential_cost_savings_monthly": 0
            }
        
        total_size = sum(ds.size_gb for ds in candidates)
        total_cost = sum(ds.storage_cost_per_month for ds in candidates)
        
        return {
            "candidates": candidates,
            "potential_savings_gb": total_size,
            "potential_cost_savings_monthly": total_cost,
            "potential_cost_savings_annual": total_cost * 12
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert datasets to DataFrame"""
        return self.repository.to_dataframe()

