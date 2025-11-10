#!/usr/bin/env python3
"""Test refusal cases"""
import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def test_refusal(message, description):
    """Test that invalid requests are properly refused"""
    session_id = f"test-{int(time.time() * 1000)}"
    
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    print(f"Message: {message}")
    
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={"message": message, "session_id": session_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        if not data.get("chart_url"):
            print(f"✅ PASS - Correctly refused")
            print(f"   Response: {data.get('response')}")
            return True
        else:
            print(f"❌ FAIL - Should have refused but created chart")
            return False
    else:
        print(f"❌ ERROR - HTTP {response.status_code}")
        return False

def main():
    print("\n" + "="*70)
    print("REFUSAL TEST SUITE")
    print("="*70)
    
    test_cases = [
        ("What's the weather today?", "General question"),
        ("Help me write an essay", "Non-chart task"),
        ("Make a pie chart with data", "Unsupported chart type"),
        ("Tell me a joke", "Off-topic request"),
        ("What is 2+2?", "Math question"),
    ]
    
    results = []
    for message, description in test_cases:
        result = test_refusal(message, description)
        results.append(result)
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
