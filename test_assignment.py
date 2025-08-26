#!/usr/bin/env python3
"""
HealthSync Assignment Testing Script
Validates all assignment requirements are met
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    try:
        # Increased timeout and added retry logic
        for attempt in range(3):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=15)
                if response.status_code == 200:
                    print("✅ Backend is healthy")
                    return True
                else:
                    print(f"❌ Backend health check failed: {response.status_code}")
                    return False
            except requests.exceptions.Timeout:
                if attempt < 2:
                    print(f"⏳ Backend not ready yet, retrying in 5 seconds... (attempt {attempt + 1}/3)")
                    time.sleep(5)
                else:
                    print("❌ Backend health check timed out after 3 attempts")
                    return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_users_endpoint():
    """Test users endpoint returns 100 synthetic users"""
    print("👥 Testing users endpoint...")
    try:
        # Increased timeout for users endpoint
        response = requests.get(f"{BASE_URL}/users", timeout=20)
        if response.status_code == 200:
            users = response.json()
            if len(users) >= 100:
                print(f"✅ Users endpoint working: {len(users)} users found")
                # Check user structure - accept both full profiles and basic IDs
                if users and all('id' in user for user in users[:5]):
                    print("✅ User data structure correct")
                    return True
                else:
                    print("❌ User data structure incomplete")
                    return False
            else:
                print(f"❌ Insufficient users: {len(users)} found, need 100")
                return False
        else:
            print(f"❌ Users endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Users endpoint timed out")
        return False
    except Exception as e:
        print(f"❌ Users endpoint error: {e}")
        return False

def test_greeting_agent():
    """Test greeting agent functionality"""
    print("👋 Testing greeting agent...")
    try:
        response = requests.get(f"{BASE_URL}/greet/1", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data or 'ok' in data:
                print("✅ Greeting agent working")
                return True
            else:
                print("❌ Greeting agent response format incorrect")
                return False
        else:
            print(f"❌ Greeting agent failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Greeting agent timed out")
        return False
    except Exception as e:
        print(f"❌ Greeting agent error: {e}")
        return False

def test_mood_agent():
    """Test mood tracking agent"""
    print("😊 Testing mood agent...")
    try:
        response = requests.post(f"{BASE_URL}/mood", 
                               json={"user_id": 1, "mood": "happy"}, 
                               timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data or 'ok' in data:
                print("✅ Mood agent working")
                return True
            else:
                print("❌ Mood agent response format incorrect")
                return False
        else:
            print(f"❌ Mood agent failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Mood agent timed out")
        return False
    except Exception as e:
        print(f"❌ Mood agent error: {e}")
        return False

def test_cgm_agent():
    """Test CGM agent"""
    print("🩸 Testing CGM agent...")
    try:
        response = requests.post(f"{BASE_URL}/cgm", 
                               json={"user_id": 1, "reading": 120}, 
                               timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data or 'ok' in data:
                print("✅ CGM agent working")
                return True
            else:
                print("❌ CGM agent response format incorrect")
                return False
        else:
            print(f"❌ CGM agent failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ CGM agent timed out")
        return False
    except Exception as e:
        print(f"❌ CGM agent error: {e}")
        return False

def test_food_agent():
    """Test food intake agent"""
    print("🍽️ Testing food agent...")
    try:
        response = requests.post(f"{BASE_URL}/food", 
                               json={"user_id": 1, "description": "rice and dal"}, 
                               timeout=20)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data or 'ok' in data:
                print("✅ Food agent working")
                return True
            else:
                print("❌ Food agent response format incorrect")
                return False
        else:
            print(f"❌ Food agent failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Food agent timed out")
        return False
    except Exception as e:
        print(f"❌ Food agent error: {e}")
        return False

def test_meal_planner_agent():
    """Test meal planner agent"""
    print("📋 Testing meal planner agent...")
    try:
        response = requests.post(f"{BASE_URL}/mealplan", 
                               json={"user_id": 1}, 
                               timeout=25)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data or 'suggestions' in data:
                print("✅ Meal planner agent working")
                return True
            else:
                print("❌ Meal planner agent response format incorrect")
                return False
        else:
            print(f"❌ Meal planner agent failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Meal planner agent timed out")
        return False
    except Exception as e:
        print(f"❌ Meal planner agent error: {e}")
        return False

def test_chat_agent():
    """Test interrupt/chat agent"""
    print("💬 Testing chat agent...")
    try:
        response = requests.post(f"{BASE_URL}/interrupt", 
                               json={"query": "Hello"}, 
                               timeout=20)
        if response.status_code == 200:
            data = response.json()
            if 'message' in data or 'ok' in data:
                print("✅ Chat agent working")
                return True
            else:
                print("❌ Chat agent response format incorrect")
                return False
        else:
            print(f"❌ Chat agent failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Chat agent timed out")
        return False
    except Exception as e:
        print(f"❌ Chat agent error: {e}")
        return False

def test_history_endpoints():
    """Test history endpoints for charts"""
    print("📊 Testing history endpoints...")
    endpoints = ['mood', 'cgm', 'food']
    success = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}/history/{endpoint}/1", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint} history endpoint working")
            else:
                print(f"❌ {endpoint} history endpoint failed: {response.status_code}")
                success = False
        except Exception as e:
            print(f"❌ {endpoint} history endpoint error: {e}")
            success = False
    
    return success

def test_file_structure():
    """Test required files exist"""
    print("📁 Testing file structure...")
    required_files = [
        "agno.yaml",
        "docker-compose.yml",
        "Dockerfile.backend",
        "Dockerfile.frontend",
        "README_ASSIGNMENT.md",
        "docs/agent-specs.md",
        "agno_agents/greeting_agent.py",
        "agno_agents/mood_agent.py",
        "agno_agents/cgm_agent.py",
        "agno_agents/food_agent.py",
        "agno_agents/meal_planner_agent.py",
        "agno_agents/interrupt_agent.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_agno_configuration():
    """Test Agno configuration"""
    print("⚙️ Testing Agno configuration...")
    try:
        with open("agno.yaml", "r") as f:
            config = f.read()
            if "greeting_agent" in config and "mood_tracker_agent" in config:
                print("✅ Agno configuration valid")
                return True
            else:
                print("❌ Agno configuration incomplete")
                return False
    except Exception as e:
        print(f"❌ Agno configuration error: {e}")
        return False

def main():
    """Run all assignment tests"""
    print("🚀 HealthSync Assignment Testing")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("File Structure", test_file_structure),
        ("Agno Configuration", test_agno_configuration),
        ("Users Endpoint", test_users_endpoint),
        ("Greeting Agent", test_greeting_agent),
        ("Mood Agent", test_mood_agent),
        ("CGM Agent", test_cgm_agent),
        ("Food Agent", test_food_agent),
        ("Meal Planner Agent", test_meal_planner_agent),
        ("Chat Agent", test_chat_agent),
        ("History Endpoints", test_history_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 ASSIGNMENT TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Assignment requirements met!")
        print("\n✅ Assignment is ready for submission!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000/docs")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
