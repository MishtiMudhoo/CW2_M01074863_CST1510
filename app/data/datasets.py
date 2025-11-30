import pandas as pd
from pathlib import Path

def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.

    Args:
        conn: sqlite3.Connection (or SQLAlchemy connection accepted by pandas)
        csv_path: Path to CSV file (str or Path)
        table_name: Name of the target table

    Returns:
        int: Number of rows loaded (0 if file not found or empty)
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"⚠️  CSV file not found: {csv_path}")
        return 0

    # Read CSV
    df = pd.read_csv(csv_path)
    if df.empty:
        print(f"⚠️  No rows in {csv_path.name}")
        return 0

    # Write to SQL table (append)
    try:
        df.to_sql(name=table_name, con=conn, if_exists="append", index=False)
    except Exception as e:
        print(f"❌ Error loading {csv_path.name} -> {table_name}: {e}")
        raise

    row_count = len(df)
    print(f"✅ Loaded {row_count} row(s) from {csv_path.name} into {table_name}")
    return row_count

def load_all_csv_data(conn, data_dir=Path("DATA")):
    """
    Convenience to load the three domain CSVs used in the lab.
    """
    mappings = [
        (data_dir / "cyber_incidents.csv", "cyber_incidents"),
        (data_dir / "datasets_metadata.csv", "datasets_metadata"),
        (data_dir / "it_tickets.csv", "it_tickets"),
    ]
    total = 0
    for path, table in mappings:
        total += load_csv_to_table(conn, path, table)
    print(f"✅ Total rows loaded: {total}")
    return total
