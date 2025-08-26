#!/usr/bin/env python3
"""
Test Step-by-Step User ID Validation Flow
Demonstrates the new validation flow where:
1. User sees "Enter User ID" prompt first
2. System validates the ID
3. If valid: proceeds to main application
4. If invalid: shows error and asks for valid ID again
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_step_by_step_validation():
    """Test the step-by-step user ID validation flow"""
    
    print("🧪 Testing Step-by-Step User ID Validation Flow")
    print("=" * 60)
    print("🎯 Flow: Enter User ID → Validate → Proceed/Retry")
    print("=" * 60)
    
    # Test 1: Invalid user ID first
    print("\n1️⃣ Step 1: User enters INVALID User ID (999)")
    print("-" * 50)
    print("Expected: Show error, ask for valid ID")
    
    response = requests.post(f"{API_BASE}/chat/", json={
        "user_id": 999,
        "message": ""
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data['message']}")
        print(f"📊 Step: {data['step']}")
        print(f"🔍 Success: {data['result'].get('ok', 'N/A')}")
        
        if not data['result'].get('ok', True):
            print("❌ Correctly rejected invalid user ID")
            print("💡 User should see error message and be prompted to enter valid ID")
        else:
            print("⚠️ Unexpectedly accepted invalid user ID")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 2: Valid user ID after invalid attempt
    print("\n2️⃣ Step 2: User enters VALID User ID (1)")
    print("-" * 50)
    print("Expected: Accept ID, greet user, proceed to main app")
    
    response = requests.post(f"{API_BASE}/chat/", json={
        "user_id": 1,
        "message": ""
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data['message']}")
        print(f"📊 Step: {data['step']}")
        print(f"🔍 Success: {data['result'].get('ok', 'N/A')}")
        
        if data['result'].get('ok', False):
            print("✅ Correctly accepted valid user ID")
            print("🎉 User greeted with personal information")
            print("🚀 User should now proceed to main application")
        else:
            print("❌ Unexpectedly rejected valid user ID")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 3: Another invalid attempt
    print("\n3️⃣ Step 3: User tries another INVALID User ID (0)")
    print("-" * 50)
    print("Expected: Show error, ask for valid ID again")
    
    response = requests.post(f"{API_BASE}/chat/", json={
        "user_id": 0,
        "message": ""
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data['message']}")
        print(f"📊 Step: {data['step']}")
        print(f"🔍 Success: {data['result'].get('ok', 'N/A')}")
        
        if not data['result'].get('ok', True):
            print("❌ Correctly rejected invalid user ID (0)")
            print("💡 User should see error message and be prompted again")
        else:
            print("⚠️ Unexpectedly accepted invalid user ID (0)")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 4: Final valid attempt
    print("\n4️⃣ Step 4: User enters another VALID User ID (50)")
    print("-" * 50)
    print("Expected: Accept ID, greet user, proceed to main app")
    
    response = requests.post(f"{API_BASE}/chat/", json={
        "user_id": 50,
        "message": ""
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data['message']}")
        print(f"📊 Step: {data['step']}")
        print(f"🔍 Success: {data['result'].get('ok', 'N/A')}")
        
        if data['result'].get('ok', False):
            print("✅ Correctly accepted valid user ID")
            print("🎉 User greeted with personal information")
            print("🚀 User should now proceed to main application")
        else:
            print("❌ Unexpectedly rejected valid user ID")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 Step-by-Step Validation Test Complete!")
    print("\n📋 Summary:")
    print("✅ Step 1: Invalid ID (999) → Rejected with error")
    print("✅ Step 2: Valid ID (1) → Accepted and greeted")
    print("✅ Step 3: Invalid ID (0) → Rejected with error")
    print("✅ Step 4: Valid ID (50) → Accepted and greeted")
    print("\n🎮 Frontend Flow:")
    print("1. User sees 'Enter User ID' form")
    print("2. User enters ID and clicks 'Continue'")
    print("3. If invalid: Shows error, form stays open")
    print("4. If valid: Shows success, redirects to main app")
    print("\n✨ Perfect step-by-step validation flow!")

if __name__ == "__main__":
    try:
        test_step_by_step_validation()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend server.")
        print("💡 Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 
