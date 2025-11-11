#!/usr/bin/env python3
"""
Test fallback agent by temporarily disabling OpenAI API key
"""
import requests
import json
import time
import os
import subprocess
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_chat_request(message: str, session_id: str, test_name: str):
    """Send a chat request and display results"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Message: {message}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "session_id": session_id},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response']}")
            print(f"Chart URL: {data.get('chart_url', 'None')}")
            if data.get('chart_url'):
                print("✅ Chart generated successfully")
            else:
                print("ℹ️  No chart (expected for refusals)")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def wait_for_backend(max_retries=10):
    """Wait for backend to be ready"""
    print("\nWaiting for backend to be ready...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready")
                return True
        except:
            if i < max_retries - 1:
                print(f"  Waiting... ({i+1}/{max_retries})")
                time.sleep(2)
    print("❌ Backend not available")
    return False

def check_agent_mode():
    """Check which agent mode is active"""
    print("\nChecking agent mode...")
    time.sleep(2)  # Wait for logs
    
    try:
        result = subprocess.run(
            ["docker", "compose", "logs", "backend", "--tail=50"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "OpenAI client initialized successfully" in result.stdout:
            print("🤖 Using: OpenAI Agent")
            return "OpenAI"
        elif "No OpenAI API key found" in result.stdout or "Using fallback" in result.stdout:
            print("🔧 Using: Fallback Rule-Based Agent")
            return "Fallback"
        else:
            print("❓ Agent mode unclear")
            return "Unknown"
    except Exception as e:
        print(f"Could not check agent mode: {e}")
        return "Unknown"

def run_tests(mode_name: str):
    """Run test suite"""
    print(f"\n{'#'*70}")
    print(f"# Testing {mode_name} Mode")
    print(f"{'#'*70}")
    
    session_id = f"test-fallback-{int(time.time())}"
    
    tests = [
        ("Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175", "Basic bar chart", True),
        ("Make a line chart with Jan=50, Feb=60, Mar=70, Apr=80", "Line chart", True),
        ("Show me 2020=100, 2021=150, 2022=200", "Year data", True),
        ("Chart: Apple=25, Banana=30, Orange=20", "Categorical", True),
        ("What's the weather?", "Refusal test", True),
    ]
    
    passed = 0
    failed = 0
    
    for message, test_name, expected_success in tests:
        result = test_chat_request(message, session_id, test_name)
        if result == expected_success:
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)
    
    # Clean up
    try:
        requests.delete(f"{BASE_URL}/api/chat/{session_id}")
    except:
        pass
    
    print(f"\n{'='*70}")
    print(f"RESULTS for {mode_name}")
    print(f"{'='*70}")
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    return passed, failed

def main():
    print("\n" + "="*70)
    print(" FALLBACK AGENT TEST")
    print("="*70)
    print("\nThis test will:")
    print("1. Test with current configuration")
    print("2. Temporarily disable OpenAI key")
    print("3. Test with fallback agent")
    print("4. Restore original configuration")
    
    # Backup original .env
    env_file = Path("/workspaces/fd-agents/backend/.env")
    backup_file = Path("/workspaces/fd-agents/backend/.env.backup")
    
    if not env_file.exists():
        print("\n❌ .env file not found")
        return
    
    # Read original content
    with open(env_file) as f:
        original_content = f.read()
    
    # Backup
    with open(backup_file, 'w') as f:
        f.write(original_content)
    
    try:
        # Test 1: Current mode (should be OpenAI)
        print("\n" + "="*70)
        print("STEP 1: Testing with current configuration")
        print("="*70)
        
        if not wait_for_backend():
            return
        
        mode = check_agent_mode()
        passed1, failed1 = run_tests(mode)
        
        # Test 2: Fallback mode
        print("\n" + "="*70)
        print("STEP 2: Testing with fallback agent (no API key)")
        print("="*70)
        
        print("\n📝 Temporarily removing OpenAI API key...")
        
        # Comment out API key
        modified_content = original_content.replace(
            "OPENAI_API_KEY=",
            "# OPENAI_API_KEY="
        )
        
        with open(env_file, 'w') as f:
            f.write(modified_content)
        
        print("🔄 Restarting backend...")
        subprocess.run(["docker", "compose", "restart", "backend"], check=True)
        
        if not wait_for_backend():
            print("⚠️  Backend failed to restart")
        else:
            mode = check_agent_mode()
            passed2, failed2 = run_tests(mode)
        
    finally:
        # Restore original .env
        print("\n" + "="*70)
        print("CLEANUP: Restoring original configuration")
        print("="*70)
        
        with open(env_file, 'w') as f:
            f.write(original_content)
        
        if backup_file.exists():
            backup_file.unlink()
        
        print("🔄 Restarting backend with original configuration...")
        subprocess.run(["docker", "compose", "restart", "backend"], check=True)
        
        print("\n✅ Configuration restored")
    
    print("\n" + "="*70)
    print(" FINAL SUMMARY")
    print("="*70)
    print(f"OpenAI Mode: {passed1} passed, {failed1} failed")
    print(f"Fallback Mode: {passed2} passed, {failed2} failed")
    
    if failed1 == 0 and failed2 == 0:
        print("\n🎉 ALL TESTS PASSED IN BOTH MODES!")
    else:
        print(f"\n⚠️  Some tests failed")

if __name__ == "__main__":
    main()
