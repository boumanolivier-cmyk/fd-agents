#!/usr/bin/env python3
"""
Test fallback agent by setting empty API key in docker
"""
import requests
import time
import subprocess
import os

BASE_URL = "http://localhost:8000"

def test_basic_functionality(mode_name: str):
    """Test basic chart generation"""
    print(f"\n{'='*70}")
    print(f"Testing {mode_name}")
    print(f"{'='*70}")
    
    session_id = f"test-{int(time.time())}"
    
    tests = [
        "Create a bar chart: Q1=100, Q2=150, Q3=200",
        "Make a line chart with Jan=50, Feb=60, Mar=70",
        "Chart: Apple=25, Banana=30",
        "What's the weather?",  # Should refuse
    ]
    
    passed = 0
    
    for test_msg in tests:
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": test_msg, "session_id": session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test_msg[:40]}: {data['response'][:50]}")
                passed += 1
            else:
                print(f"❌ {test_msg[:40]}: Failed")
        except Exception as e:
            print(f"❌ {test_msg[:40]}: {str(e)[:50]}")
        
        time.sleep(0.5)
    
    # Cleanup
    try:
        requests.delete(f"{BASE_URL}/api/chat/{session_id}")
    except:
        pass
    
    print(f"\nResult: {passed}/{len(tests)} passed")
    return passed == len(tests)

def wait_for_backend():
    """Wait for backend"""
    print("Waiting for backend...")
    for i in range(15):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Backend ready")
                return True
        except:
            print(f"  Waiting... {i+1}/15")
            time.sleep(2)
    return False

def check_logs_for_agent():
    """Check which agent is active"""
    time.sleep(2)
    result = subprocess.run(
        ["docker", "compose", "logs", "backend", "--tail=30"],
        capture_output=True,
        text=True
    )
    
    if "OpenAI client initialized" in result.stdout:
        return "OpenAI"
    elif "fallback" in result.stdout.lower() or "no openai" in result.stdout.lower():
        return "Fallback"
    return "Unknown"

def main():
    print("="*70)
    print(" AGENT MODE TESTING")
    print("="*70)
    
    # Test current setup
    print("\n1. Testing current setup (with API key)...")
    if wait_for_backend():
        agent_mode = check_logs_for_agent()
        print(f"Current agent: {agent_mode}")
        result1 = test_basic_functionality(f"Current Setup ({agent_mode})")
    else:
        print("❌ Backend not available")
        return
    
    # Test with env override (no rebuild needed)
    print("\n2. Testing with empty API key override...")
    print("   Stopping backend...")
    subprocess.run(["docker", "compose", "stop", "backend"], check=True)
    
    print("   Starting backend with empty OPENAI_API_KEY...")
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = ""
    
    subprocess.Popen(
        ["docker", "compose", "up", "backend"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if wait_for_backend():
        agent_mode = check_logs_for_agent()
        print(f"Current agent: {agent_mode}")
        result2 = test_basic_functionality(f"Fallback Mode ({agent_mode})")
    else:
        print("❌ Backend not available")
        result2 = False
    
    # Restore
    print("\n3. Restoring normal operation...")
    subprocess.run(["docker", "compose", "restart", "backend"], check=True)
    
    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    print(f"With API Key: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Without API Key (Fallback): {'✅ PASS' if result2 else '❌ FAIL'}")
    
    if result1 and result2:
        print("\n🎉 Both modes work correctly!")
    else:
        print("\n⚠️  Some tests failed")

if __name__ == "__main__":
    main()
