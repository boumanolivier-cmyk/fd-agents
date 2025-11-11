#!/usr/bin/env python3
"""
Test chart agent with both OpenAI and fallback models
"""
import requests
import json
import time
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
            print(f"Chart Type: {data.get('chart_id', 'None')}")
            print(f"Color Scheme: {data.get('color_scheme', 'None')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def run_test_suite(agent_type: str):
    """Run a comprehensive test suite"""
    print(f"\n{'#'*70}")
    print(f"# Testing with {agent_type} Agent")
    print(f"{'#'*70}")
    
    session_id = f"test-{agent_type.lower()}-{int(time.time())}"
    
    tests = [
        ("Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175", "Basic bar chart"),
        ("Make a line chart with Jan=50, Feb=60, Mar=70, Apr=80, May=90", "Line chart with time data"),
        ("Chart these values: Apple=25, Banana=30, Orange=20", "Categorical data"),
        ("Show me a chart with 2020=100, 2021=150, 2022=200, 2023=250", "Year-based data"),
        ("What's the weather today?", "Refusal test - weather"),
        ("Can you make a pie chart?", "Refusal test - pie chart"),
    ]
    
    passed = 0
    failed = 0
    
    for message, test_name in tests:
        if test_chat_request(message, session_id, test_name):
            passed += 1
        else:
            failed += 1
        time.sleep(1)  # Small delay between requests
    
    # Test style change (requires conversation history)
    print(f"\n{'='*70}")
    print(f"TEST: Style change request")
    print(f"{'='*70}")
    print(f"Message: Change it to BNR colors")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "Change it to BNR colors", "session_id": session_id},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Response: {data['response']}")
            print(f"Color Scheme: {data.get('color_scheme', 'None')}")
            if data.get('color_scheme') == 'bnr':
                print("✅ Color scheme correctly changed to BNR")
                passed += 1
            else:
                print("⚠️  Color scheme not as expected")
                failed += 1
        else:
            print(f"Status: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ Exception: {e}")
        failed += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY for {agent_type} Agent")
    print(f"{'='*70}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    # Clean up session
    requests.delete(f"{BASE_URL}/api/chat/{session_id}")
    
    return passed, failed

def main():
    print("\n" + "="*70)
    print(" CHART AGENT TEST SUITE - OpenAI vs Fallback")
    print("="*70)
    
    # Wait for backend to be ready
    print("\nChecking backend availability...")
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Backend is ready")
                break
        except:
            if i < max_retries - 1:
                print(f"Waiting for backend... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("❌ Backend not available")
                return
    
    # Check which agent is being used
    print("\nChecking agent configuration...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "Create a bar chart: A=1, B=2", "session_id": "config-check"},
            timeout=10
        )
        # Clean up
        requests.delete(f"{BASE_URL}/api/chat/config-check")
        
        # Check logs to determine which agent was used
        print("Agent type will be determined from logs")
    except Exception as e:
        print(f"Could not determine agent type: {e}")
    
    # Run test suite
    agent_type = "Current"  # Will show which agent is actually being used
    passed, failed = run_test_suite(agent_type)
    
    print(f"\n{'='*70}")
    print(" FINAL RESULTS")
    print(f"{'='*70}")
    print(f"Total Passed: {passed}")
    print(f"Total Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} tests failed")

if __name__ == "__main__":
    main()
