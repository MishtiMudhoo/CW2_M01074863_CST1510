"""
Database Initialization Utility
Ensures database tables are created
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for app imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.data.db import connect_database
from app.data.schema import create_all_tables


def ensure_database_initialized():
    """Ensure all database tables are created"""
    try:
        conn = connect_database()
        create_all_tables(conn)
        conn.close()
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

