import sqlite3
import streamlit as st
from app.data.schema import create_all_tables

DB_PATH = "app/data/database.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

st.title("CW2 - Hello Streamlit")

if st.button("Create all tables"):
    conn = get_conn()
    create_all_tables(conn)
    conn.close()
    st.success("Tables created (or already existed).")

conn = get_conn()
cursor = conn.cursor()

# show tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [r["name"] for r in cursor.fetchall()]
st.write("Tables found:", tables)

# show users table content (if exists)
if "users" in tables:
    cursor.execute("SELECT id, username, role FROM users;")
    rows = cursor.fetchall()
    st.write("Users:")
    st.table([dict(row) for row in rows])
else:
    st.info("No users table yet. Click 'Create all tables' to create it.")

conn.close()