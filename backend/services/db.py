import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "healthcare.db"

def ensure_tables():
    ensure_log_tables()
    
def initialize_with_sample_data():
    """Initialize database with sample data if empty"""
    con = get_db()
    cur = con.cursor()
    
    # Check if users table has data with proper schema
    try:
        cur.execute("SELECT COUNT(*) FROM users WHERE first_name IS NOT NULL")
        count = cur.fetchone()[0]
        if count == 0:
            print("No users with full schema found, running data generation...")
            # Run the user generation script
            import subprocess
            import sys
            import os
            script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'generate_users.py')
            result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
            print("✅ Sample users generated")
            print(f"Generation output: {result.stdout}")
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        con.close()

def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def get_db_connection():
    """Get a database connection that can be used in a context manager"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def ensure_log_tables() -> None:
    con = get_db(); cur = con.cursor()
    # Create users table if not exists (for compatibility)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            city TEXT,
            dietary_preference TEXT,
            medical_conditions TEXT,
            physical_limitations TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ts TEXT,
            mood TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cgm_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ts TEXT,
            reading REAL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS food_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ts TEXT,
            description TEXT
        )
    """)
    
    # Aliases for compatibility with seed.py
    cur.execute("""
        CREATE VIEW IF NOT EXISTS mood AS 
        SELECT id, user_id, ts, mood FROM mood_logs
    """)
    cur.execute("""
        CREATE VIEW IF NOT EXISTS cgm AS 
        SELECT id, user_id, ts, reading FROM cgm_logs
    """)
    cur.execute("""
        CREATE VIEW IF NOT EXISTS food AS 
        SELECT id, user_id, ts, description FROM food_logs
    """)
    
    con.commit(); con.close()

def get_user(user_id: int) -> Dict[str, Any]:
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cur.fetchone(); con.close()
    return dict(row) if row else {}

def insert_mood(user_id: int, mood: str, ts: str) -> None:
    con = get_db(); cur = con.cursor()
    cur.execute("INSERT INTO mood_logs(user_id, timestamp, mood) VALUES(?,?,?)", (user_id, ts, mood))
    con.commit(); con.close()

def insert_cgm(user_id: int, reading: float, ts: str) -> None:
    con = get_db(); cur = con.cursor()
    cur.execute("INSERT INTO cgm_logs(user_id, glucose_level, timestamp) VALUES(?,?,?)", (user_id, reading, ts))
    con.commit(); con.close()

def insert_food(user_id: int, description: str, ts: str) -> None:
    con = get_db(); cur = con.cursor()
    cur.execute("INSERT INTO food_logs(user_id, meal_description, timestamp) VALUES(?,?,?)", (user_id, description, ts))
    con.commit(); con.close()

def get_mood_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT timestamp, mood FROM mood_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    rows = [dict(r) for r in cur.fetchall()]; con.close()
    return rows

def get_cgm_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT timestamp, glucose_level FROM cgm_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    rows = [dict(r) for r in cur.fetchall()]; con.close()
    return rows

def get_food_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT timestamp, meal_description FROM food_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    rows = [dict(r) for r in cur.fetchall()]; con.close()
    return rows

def get_latest_cgm_for_user(user_id: int):
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT glucose_level FROM cgm_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", (user_id,))
    row = cur.fetchone(); con.close()
    return float(row["glucose_level"]) if row else None
