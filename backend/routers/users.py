import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from backend.services.db import get_db

router = APIRouter(prefix="/users", tags=["👥 User Management"])

class User(BaseModel):
    """User profile model"""
    id: int = Field(..., description="User ID")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name") 
    city: Optional[str] = Field(None, description="City location")
    dietary_preference: Optional[str] = Field(None, description="Dietary preference")
    medical_conditions: Optional[str] = Field(None, description="Medical conditions (JSON)")

@router.get("", response_model=List[User])
def list_users() -> List[User]:
    """
    👥 **Get All Users**
    
    Returns a list of all users in the system with full profile information.
    Includes ID, name, location, dietary preferences, and medical conditions.
    
    **Returns:** Array of user objects with complete profile data
    
    **Note:** If no users exist, creates 100 demo users automatically
    """
    # Use direct database connection to avoid threading issues
    from backend.services.db import get_db_connection
    
    try:
        with get_db_connection() as db:
            cur = db.cursor()

            # First, ensure the users table exists with proper schema
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    city TEXT,
                    dietary_preference TEXT,
                    medical_conditions TEXT,
                    physical_limitations TEXT,
                    name TEXT
                )
            """)
            
            # Check if we have users with full schema
            cur.execute("SELECT COUNT(*) FROM users WHERE first_name IS NOT NULL")
            full_users_count = cur.fetchone()[0]
            
            if full_users_count == 0:
                # No full users found, trigger data generation
                print("No full user data found, generating users...")
                import subprocess
                import sys
                import os
                script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'generate_users.py')
                try:
                    subprocess.run([sys.executable, script_path], check=True)
                except Exception as e:
                    print(f"Error generating users: {e}")
            
            # Now fetch the full user data
            cur.execute("""
                SELECT id, first_name, last_name, city, dietary_preference, medical_conditions
                FROM users 
                WHERE first_name IS NOT NULL
                ORDER BY id LIMIT 100
            """)
            
            users = []
            for row in cur.fetchall():
                users.append(User(
                    id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    city=row[3],
                    dietary_preference=row[4],
                    medical_conditions=row[5]
                ))
            
            if users:
                return users

            # Fallback: create simple demo users if generation failed
            simple_users = []
            for i in range(1, 101):
                simple_users.append(User(
                    id=i,
                    first_name=f"User",
                    last_name=f"{i}",
                    city="Demo City",
                    dietary_preference="mixed",
                    medical_conditions="[]"
                ))
            
            return simple_users
            
    except Exception as e:
        print(f"Error in list_users: {e}")
        # Emergency fallback
        return [User(
            id=1,
            first_name="Demo",
            last_name="User",
            city="Demo City", 
            dietary_preference="mixed",
            medical_conditions="[]"
        )]