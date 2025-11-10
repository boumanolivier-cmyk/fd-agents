#!/usr/bin/env python3
"""Comprehensive test script for chart generation"""
import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def test_case(message, description):
    """Run a single test case"""
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
        if data.get("chart_url"):
            print(f"✅ PASS - Chart created: {data.get('chart_id')}")
            print(f"   Response: {data.get('response')}")
            return True
        else:
            print(f"❌ FAIL - No chart created")
            print(f"   Response: {data.get('response')}")
            return False
    else:
        print(f"❌ ERROR - HTTP {response.status_code}")
        return False

def main():
    print("\n" + "="*70)
    print("CHART GENERATION TEST SUITE")
    print("="*70)
    
    test_cases = [
        ("Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175", "Basic quarterly data with explicit bar chart request"),
        ("Make a line chart with 2020=50, 2021=75, 2022=100, 2023=125", "Year-based time series data"),
        ("Chart this data: Apple=25, Banana=30, Orange=20, Grape=15", "Categorical data (should be bar)"),
        ("Show sales: Jan=100, Feb=120, Mar=110, Apr=130, May=140", "Monthly time series"),
        ("Create chart: Product A=500, Product B=750, Product C=600", "Product comparison"),
    ]
    
    results = []
    for message, description in test_cases:
        result = test_case(message, description)
        results.append(result)
        time.sleep(1)  # Small delay between tests
    
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
