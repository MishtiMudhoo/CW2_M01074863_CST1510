"""
Dataset Repository
Handles dataset catalog data using database or in-memory storage
"""

import sys
import os
from typing import List, Optional
from pathlib import Path
from datetime import datetime, date
import pandas as pd

# Add parent directory to path for app imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.data.db import connect_database
from ..models.dataset import Dataset


class DatasetRepository:
    """Repository for dataset catalog data"""
    
    def __init__(self, datasets: List[Dataset] = None, use_database: bool = True):
        """
        Initialize repository
        
        Args:
            datasets: List of datasets (defaults to empty list or loads from DB)
            use_database: If True, load from database; if False, use provided datasets
        """
        if use_database:
            self._datasets = self._load_from_database()
        else:
            self._datasets = datasets if datasets is not None else []
    
    def _load_from_database(self) -> List[Dataset]:
        """Load datasets from database"""
        try:
            conn = connect_database()
            df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
            conn.close()
            
            if df.empty:
                return []
            
            datasets = []
            for _, row in df.iterrows():
                # Map database columns to model
                # Database: dataset_name, category, source, last_updated, record_count, file_size_mb
                # Model: name, department, size_gb, rows_millions, upload_date, last_accessed, etc.
                try:
                    last_updated = pd.to_datetime(row.get('last_updated', datetime.now())).date()
                    upload_date = pd.to_datetime(row.get('created_at', datetime.now())).date() if 'created_at' in row else last_updated
                    
                    size_gb = (row.get('file_size_mb', 0) / 1024) if 'file_size_mb' in row else 0
                    rows_millions = (row.get('record_count', 0) / 1_000_000) if 'record_count' in row else 0
                    
                    dataset = Dataset(
                        name=row.get('dataset_name', 'Unknown'),
                        department=row.get('source', row.get('category', 'Unknown')),
                        size_gb=round(size_gb, 2),
                        rows_millions=round(rows_millions, 2),
                        upload_date=upload_date,
                        last_accessed=last_updated,
                        days_since_access=(datetime.now().date() - last_updated).days,
                        quality_status="Passed",  # Default, not in DB
                        dependencies=0,  # Default, not in DB
                        access_frequency_30d=0,  # Default, not in DB
                        storage_cost_per_month=round(size_gb * 0.023, 2)
                    )
                    dataset.calculate_archive_score()
                    datasets.append(dataset)
                except Exception as e:
                    print(f"Error loading dataset {row.get('id', 'unknown')}: {e}")
                    continue
            return datasets
        except Exception as e:
            print(f"Error loading datasets from database: {e}")
            return []
    
    def add(self, dataset: Dataset) -> None:
        """Add a dataset to the repository"""
        self._datasets.append(dataset)
    
    def add_all(self, datasets: List[Dataset]) -> None:
        """Add multiple datasets"""
        self._datasets.extend(datasets)
    
    def get_all(self) -> List[Dataset]:
        """Get all datasets"""
        return self._datasets.copy()
    
    def get_by_department(self, department: str) -> List[Dataset]:
        """Get datasets by department"""
        return [ds for ds in self._datasets if ds.department == department]
    
    def get_by_quality_status(self, status: str) -> List[Dataset]:
        """Get datasets by quality status"""
        return [ds for ds in self._datasets if ds.quality_status == status]
    
    def get_stale_datasets(self, days_threshold: int = 90) -> List[Dataset]:
        """Get stale datasets (not accessed in threshold days)"""
        return [ds for ds in self._datasets if ds.is_stale(days_threshold)]
    
    def get_rarely_accessed(self, threshold: int = 5) -> List[Dataset]:
        """Get rarely accessed datasets"""
        return [ds for ds in self._datasets if ds.is_rarely_accessed(threshold)]
    
    def get_top_consumers(self, limit: int = 5) -> List[Dataset]:
        """Get top resource-consuming datasets"""
        sorted_datasets = sorted(self._datasets, key=lambda x: x.size_gb, reverse=True)
        return sorted_datasets[:limit]
    
    def get_archive_candidates(self, limit: int = 5) -> List[Dataset]:
        """Get top archiving candidates"""
        # Calculate archive scores if not already calculated
        for dataset in self._datasets:
            if dataset.archive_score is None:
                dataset.calculate_archive_score()
        
        sorted_datasets = sorted(self._datasets, key=lambda x: x.archive_score or 0, reverse=True)
        return sorted_datasets[:limit]
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert datasets to pandas DataFrame"""
        if not self._datasets:
            return pd.DataFrame()
        return pd.DataFrame([ds.to_dict() for ds in self._datasets])
    
    def get_total_storage(self) -> float:
        """Get total storage in GB"""
        return sum(ds.size_gb for ds in self._datasets)
    
    def get_total_cost(self) -> float:
        """Get total monthly storage cost"""
        return sum(ds.storage_cost_per_month for ds in self._datasets)

