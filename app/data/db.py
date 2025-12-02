import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    
    #check if data folder exists, else create data folder
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Created the data folder")

    print(f"Connecting to database at: {db_path}")
    return sqlite3.connect(str(db_path))
