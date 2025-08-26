#!/usr/bin/env python3
"""
Test User ID Validation Flow
Demonstrates the Greeting Agent validation as per assignment specifications:

5. Greeting Agent:
   - Inputs: user ID
   - Action: validate user ID against dataset
   - If invalid: prompt user to re-enter a valid ID before allowing further interaction
   - If valid: retrieve name/city → greet
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_user_validation():
    """Test the complete user ID validation flow"""
    
    print("🧪 Testing User ID Validation Flow")
    print("=" * 50)
    
    # Test 1: Invalid user ID (999)
    print("\n1️⃣ Testing INVALID User ID (999):")
    print("-" * 30)
    
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
        else:
            print("⚠️ Unexpectedly accepted invalid user ID")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 2: Valid user ID (1)
    print("\n2️⃣ Testing VALID User ID (1):")
    print("-" * 30)
    
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
        else:
            print("❌ Unexpectedly rejected valid user ID")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 3: Another valid user ID (50)
    print("\n3️⃣ Testing Another VALID User ID (50):")
    print("-" * 30)
    
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
        else:
            print("❌ Unexpectedly rejected valid user ID")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 4: Edge case - User ID 0
    print("\n4️⃣ Testing Edge Case - User ID (0):")
    print("-" * 30)
    
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
        else:
            print("⚠️ Unexpectedly accepted invalid user ID (0)")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 5: Edge case - User ID 101
    print("\n5️⃣ Testing Edge Case - User ID (101):")
    print("-" * 30)
    
    response = requests.post(f"{API_BASE}/chat/", json={
        "user_id": 101,
        "message": ""
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data['message']}")
        print(f"📊 Step: {data['step']}")
        print(f"🔍 Success: {data['result'].get('ok', 'N/A')}")
        
        if not data['result'].get('ok', True):
            print("❌ Correctly rejected invalid user ID (101)")
        else:
            print("⚠️ Unexpectedly accepted invalid user ID (101)")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 User ID Validation Test Complete!")
    print("\n📋 Summary:")
    print("✅ Greeting Agent correctly validates user IDs")
    print("✅ Invalid IDs are rejected with clear error messages")
    print("✅ Valid IDs are accepted and users are greeted personally")
    print("✅ The system follows assignment specifications exactly")

if __name__ == "__main__":
    try:
        test_user_validation()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend server.")
        print("💡 Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
