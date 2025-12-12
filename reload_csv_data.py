"""
Utility script to clear database and reload data from CSV files.
This will fix duplicate data issues.
"""
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.csv_loader import load_cyber_incidents_csv, load_it_tickets_csv, load_datasets_metadata_csv
import sys

def reload_all_csv_data():
    """Clear database tables and reload from CSV files."""
    print("="*60)
    print("RELOADING CSV DATA INTO DATABASE")
    print("="*60)
    
    conn = connect_database()
    
    # Create tables if they don't exist
    print("\n[0/4] Creating database tables...")
    create_all_tables(conn)
    print("       ✓ Tables created/verified")
    
    # Clear and reload cyber incidents
    print("\n[1/4] Reloading Cyber Incidents...")
    load_cyber_incidents_csv(conn, clear_existing=True)
    
    # Clear and reload IT tickets
    print("\n[2/4] Reloading IT Tickets...")
    load_it_tickets_csv(conn, clear_existing=True)
    
    # Clear and reload datasets metadata
    print("\n[3/4] Reloading Datasets Metadata...")
    load_datasets_metadata_csv(conn, clear_existing=True)
    
    # Verify counts
    cursor = conn.cursor()
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
    cyber_count = cursor.fetchone()[0]
    print(f"Cyber Incidents: {cyber_count} (expected: 115)")
    
    cursor.execute("SELECT COUNT(*) FROM it_tickets")
    it_count = cursor.fetchone()[0]
    print(f"IT Tickets: {it_count} (expected: 150)")
    
    cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
    dataset_count = cursor.fetchone()[0]
    print(f"Datasets: {dataset_count} (expected: 5)")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ CSV data reloaded successfully!")
    print("="*60)
    print("\n💡 Restart your Streamlit app to see the updated data.")

if __name__ == "__main__":
    # Allow non-interactive mode with --yes flag
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        reload_all_csv_data()
    else:
        response = input("This will clear all existing data and reload from CSV. Continue? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            reload_all_csv_data()
        else:
            print("Cancelled.")

