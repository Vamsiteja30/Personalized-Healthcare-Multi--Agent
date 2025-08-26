#!/usr/bin/env python3
"""
Debug script for user data
Assignment: Personalized Healthcare Multi-Agent Demo
"""

import sqlite3
import os
from pathlib import Path

def debug_users():
    """Debug user data in the database"""
    
    # Database path
    db_path = Path("data/healthcare.db")
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    print(f"🔍 Debugging database: {db_path}")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 Tables in database:")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # Check users table
        print("👥 Users table structure:")
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        print("\n" + "=" * 50)
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"📊 Total users: {user_count}")
        
        # Show sample users
        print("\n👤 Sample users:")
        cursor.execute("SELECT id, first_name, last_name, city, dietary_preference FROM users LIMIT 5;")
        users = cursor.fetchall()
        
        for user in users:
            print(f"   - ID: {user[0]}, Name: {user[1]} {user[2]}, City: {user[3]}, Diet: {user[4]}")
        
        # Check for null values
        print("\n🔍 Checking for null values:")
        cursor.execute("SELECT COUNT(*) FROM users WHERE first_name IS NULL OR last_name IS NULL;")
        null_count = cursor.fetchone()[0]
        print(f"   - Users with null names: {null_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE city IS NULL;")
        null_city = cursor.fetchone()[0]
        print(f"   - Users with null city: {null_city}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE dietary_preference IS NULL;")
        null_diet = cursor.fetchone()[0]
        print(f"   - Users with null diet: {null_diet}")
        
        # Check medical conditions
        print("\n🏥 Medical conditions distribution:")
        cursor.execute("SELECT medical_conditions, COUNT(*) FROM users GROUP BY medical_conditions;")
        conditions = cursor.fetchall()
        
        for condition, count in conditions:
            print(f"   - {condition or 'None'}: {count}")
        
        # Check physical limitations
        print("\n♿ Physical limitations distribution:")
        cursor.execute("SELECT physical_limitations, COUNT(*) FROM users GROUP BY physical_limitations;")
        limitations = cursor.fetchall()
        
        for limitation, count in limitations:
            print(f"   - {limitation or 'None'}: {count}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Debug complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_users()
