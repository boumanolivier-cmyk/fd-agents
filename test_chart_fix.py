#!/usr/bin/env python3
"""Test script to verify chart generation fix"""
import requests
import json
import time

# Backend URL
BACKEND_URL = "http://localhost:8000"

def test_chart_generation():
    """Test creating a chart with the example message"""
    
    # Create a test session
    session_id = f"test-session-{int(time.time())}"
    
    print(f"Testing with session: {session_id}")
    print("-" * 60)
    
    # Test message
    message = "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175"
    
    print(f"\nSending message: {message}")
    print("-" * 60)
    
    # Send chat request
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={
            "message": message,
            "session_id": session_id
        }
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print("-" * 60)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse Data:")
        print(json.dumps(data, indent=2))
        print("-" * 60)
        
        if data.get("chart_url"):
            print(f"\n✅ SUCCESS! Chart generated at: {data['chart_url']}")
            print(f"Chart ID: {data.get('chart_id')}")
        else:
            print(f"\n❌ FAILED: No chart URL in response")
            print(f"Response: {data.get('response')}")
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_chart_generation()
