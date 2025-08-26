import sqlite3

try:
    conn = sqlite3.connect('healthcare.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    # Check CGM data
    cursor.execute("SELECT * FROM cgm_logs LIMIT 5")
    cgm_data = cursor.fetchall()
    print("CGM data:", cgm_data)
    
    # Check mood data
    cursor.execute("SELECT * FROM mood_logs LIMIT 5")
    mood_data = cursor.fetchall()
    print("Mood data:", mood_data)
    
    # Check food data
    cursor.execute("SELECT * FROM food_logs LIMIT 5")
    food_data = cursor.fetchall()
    print("Food data:", food_data)
    
    conn.close()
except Exception as e:
    print("Error:", e)
