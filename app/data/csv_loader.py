"""
Utility functions to load CSV data into the database.
"""
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import os


def load_cyber_incidents_csv(conn, csv_path=None, clear_existing=False):
    """
    Load cyber incidents from CSV file into the database.
    
    Args:
        conn: Database connection object
        csv_path: Path to the CSV file (defaults to DATA/cyber_incidents.csv relative to project root)
        clear_existing: If True, clear existing data before loading
    """
    try:
        # Resolve CSV path relative to project root
        if csv_path is None:
            # Get project root (parent of app directory)
            project_root = Path(__file__).parent.parent.parent
            csv_path = project_root / "DATA" / "cyber_incidents.csv"
        else:
            csv_path = Path(csv_path)
            if not csv_path.is_absolute():
                # If relative, make it relative to project root
                project_root = Path(__file__).parent.parent.parent
                csv_path = project_root / csv_path
        
        if not csv_path.exists():
            print(f"       ✗ CSV file not found: {csv_path}")
            return 0
        
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0 and not clear_existing:
            print(f"       ⚠️  Database already contains {existing_count} incidents. Skipping CSV load.")
            print(f"       💡 To reload from CSV, clear the database first or set clear_existing=True")
            return 0
        
        # Clear existing data if requested
        if clear_existing and existing_count > 0:
            cursor.execute("DELETE FROM cyber_incidents")
            print(f"       🗑️  Cleared {existing_count} existing incidents")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Map CSV columns to database columns
        # CSV: incident_id, timestamp, severity, category, status, description
        # DB: date, incident_type, severity, status, description, reported_by
        
        inserted_count = 0
        for _, row in df.iterrows():
            # Extract date from timestamp (just the date part)
            timestamp = pd.to_datetime(row['timestamp'])
            date_str = timestamp.strftime('%Y-%m-%d')
            
            # Map status: Closed -> Resolved, In Progress -> In Progress, Open -> Unresolved
            status_map = {
                'Closed': 'Resolved',
                'Resolved': 'Resolved',
                'Open': 'Unresolved',
                'In Progress': 'In Progress'
            }
            db_status = status_map.get(row['status'], row['status'])
            
            # Check if this exact record already exists (to prevent duplicates)
            cursor.execute("""
                SELECT COUNT(*) FROM cyber_incidents 
                WHERE date = ? AND incident_type = ? AND severity = ? 
                AND status = ? AND description = ?
            """, (
                date_str,
                row['category'],
                row['severity'],
                db_status,
                row['description']
            ))
            
            if cursor.fetchone()[0] == 0:
                # Insert into database only if it doesn't exist
                cursor.execute("""
                    INSERT INTO cyber_incidents 
                    (date, incident_type, severity, status, description, reported_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    date_str,
                    row['category'],
                    row['severity'],
                    db_status,
                    row['description'],
                    'system'  # Default reported_by
                ))
                inserted_count += 1
        
        conn.commit()
        print(f"       ✓ Loaded {inserted_count} new cyber incidents from CSV (skipped {len(df) - inserted_count} duplicates)")
        return inserted_count
    except Exception as e:
        print(f"       ✗ Error loading cyber incidents: {str(e)}")
        return 0


def load_it_tickets_csv(conn, csv_path=None, clear_existing=False):
    """
    Load IT tickets from CSV file into the database.
    
    Args:
        conn: Database connection object
        csv_path: Path to the CSV file (defaults to DATA/it_tickets.csv relative to project root)
        clear_existing: If True, clear existing data before loading
    """
    try:
        # Resolve CSV path relative to project root
        if csv_path is None:
            # Get project root (parent of app directory)
            project_root = Path(__file__).parent.parent.parent
            csv_path = project_root / "DATA" / "it_tickets.csv"
        else:
            csv_path = Path(csv_path)
            if not csv_path.is_absolute():
                # If relative, make it relative to project root
                project_root = Path(__file__).parent.parent.parent
                csv_path = project_root / csv_path
        
        if not csv_path.exists():
            print(f"       ✗ CSV file not found: {csv_path}")
            return 0
        
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM it_tickets")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0 and not clear_existing:
            print(f"       ⚠️  Database already contains {existing_count} tickets. Skipping CSV load.")
            print(f"       💡 To reload from CSV, clear the database first or set clear_existing=True")
            return 0
        
        # Clear existing data if requested
        if clear_existing and existing_count > 0:
            cursor.execute("DELETE FROM it_tickets")
            print(f"       🗑️  Cleared {existing_count} existing tickets")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Map CSV columns to database columns
        # CSV: ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours
        # DB: ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to
        
        inserted_count = 0
        for _, row in df.iterrows():
            # Parse created_at timestamp
            created_at = pd.to_datetime(row['created_at'])
            created_date = created_at.strftime('%Y-%m-%d')
            
            # Calculate resolved_date if status is Resolved and resolution_time_hours exists
            resolved_date = None
            if row['status'] == 'Resolved' and pd.notna(row.get('resolution_time_hours')):
                resolved_at = created_at + timedelta(hours=row['resolution_time_hours'])
                resolved_date = resolved_at.strftime('%Y-%m-%d')
            
            # Extract subject from description (first 50 chars or full description)
            description = str(row['description'])
            subject = description[:50] if len(description) > 50 else description
            
            # Default category
            category = "General"
            
            ticket_id = str(row['ticket_id'])
            
            # Check if this ticket already exists (ticket_id is unique)
            cursor.execute("SELECT COUNT(*) FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
            
            if cursor.fetchone()[0] == 0:
                # Insert into database only if it doesn't exist
                cursor.execute("""
                    INSERT INTO it_tickets 
                    (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket_id,
                    row['priority'],
                    row['status'],
                    category,
                    subject,
                    description,
                    created_date,
                    resolved_date,
                    row['assigned_to']
                ))
                inserted_count += 1
        
        conn.commit()
        print(f"       ✓ Loaded {inserted_count} new IT tickets from CSV (skipped {len(df) - inserted_count} duplicates)")
        return inserted_count
    except Exception as e:
        print(f"       ✗ Error loading IT tickets: {str(e)}")
        return 0


def load_datasets_metadata_csv(conn, csv_path=None, clear_existing=False):
    """
    Load datasets metadata from CSV file into the database.
    
    Args:
        conn: Database connection object
        csv_path: Path to the CSV file (defaults to DATA/datasets_metadata.csv relative to project root)
        clear_existing: If True, clear existing data before loading
    """
    try:
        # Resolve CSV path relative to project root
        if csv_path is None:
            # Get project root (parent of app directory)
            project_root = Path(__file__).parent.parent.parent
            csv_path = project_root / "DATA" / "datasets_metadata.csv"
        else:
            csv_path = Path(csv_path)
            if not csv_path.is_absolute():
                # If relative, make it relative to project root
                project_root = Path(__file__).parent.parent.parent
                csv_path = project_root / csv_path
        
        if not csv_path.exists():
            print(f"       ✗ CSV file not found: {csv_path}")
            return 0
        
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0 and not clear_existing:
            print(f"       ⚠️  Database already contains {existing_count} datasets. Skipping CSV load.")
            print(f"       💡 To reload from CSV, clear the database first or set clear_existing=True")
            return 0
        
        # Clear existing data if requested
        if clear_existing and existing_count > 0:
            cursor.execute("DELETE FROM datasets_metadata")
            print(f"       🗑️  Cleared {existing_count} existing datasets")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Map CSV columns to database columns
        # CSV: dataset_id, name, rows, columns, uploaded_by, upload_date
        # DB: dataset_name, category, source, last_updated, record_count, file_size_mb
        
        inserted_count = 0
        for _, row in df.iterrows():
            # Parse upload_date
            upload_date = pd.to_datetime(row['upload_date'])
            last_updated = upload_date.strftime('%Y-%m-%d')
            
            # Default values for missing columns
            category = "General"
            source = "Internal"
            file_size_mb = 0.0  # Default file size
            
            dataset_name = row['name']
            
            # Check if this dataset already exists
            cursor.execute("SELECT COUNT(*) FROM datasets_metadata WHERE dataset_name = ?", (dataset_name,))
            
            if cursor.fetchone()[0] == 0:
                # Insert into database only if it doesn't exist
                cursor.execute("""
                    INSERT INTO datasets_metadata 
                    (dataset_name, category, source, last_updated, record_count, file_size_mb)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    dataset_name,
                    category,
                    source,
                    last_updated,
                    int(row['rows']),
                    file_size_mb
                ))
                inserted_count += 1
        
        conn.commit()
        print(f"       ✓ Loaded {inserted_count} new dataset metadata records from CSV (skipped {len(df) - inserted_count} duplicates)")
        return inserted_count
    except Exception as e:
        print(f"       ✗ Error loading datasets metadata: {str(e)}")
        return 0


def load_all_csv_data(conn):
    """
    Load all CSV files into the database.
    
    Args:
        conn: Database connection object
    """
    print("\n[4/5] Loading CSV data...")
    
    total_loaded = 0
    total_loaded += load_cyber_incidents_csv(conn)
    total_loaded += load_it_tickets_csv(conn)
    total_loaded += load_datasets_metadata_csv(conn)
    
    print(f"       Total: {total_loaded} records loaded from CSV files")
    return total_loaded

