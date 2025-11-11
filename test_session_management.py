#!/usr/bin/env python3
"""
Test script to verify session management:
1. Sessions are properly created and updated
2. Sessions are completely deleted on "new conversation"
3. Both chat and Excel inputs are tracked in the session
"""
import json
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
SESSION_FILE = Path("backend/data/sessions.json")

def read_sessions():
    """Read current sessions.json"""
    with open(SESSION_FILE) as f:
        return json.load(f)

def print_sessions(label):
    """Print current sessions for debugging"""
    sessions = read_sessions()
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"Number of sessions: {len(sessions)}")
    for session_id, session_data in sessions.items():
        print(f"\nSession: {session_id}")
        print(f"  Created: {session_data['created_at']}")
        print(f"  Style: {session_data['style']}")
        print(f"  Messages: {len(session_data.get('chat_history', []))}")
        for i, msg in enumerate(session_data.get('chat_history', [])):
            print(f"    {i+1}. [{msg['role']}] {msg['content'][:60]}...")
            if msg.get('metadata'):
                print(f"       Metadata: {msg['metadata'].get('type', 'N/A')}")

def test_session_lifecycle():
    """Test complete session lifecycle"""
    session_id = f"test-session-{int(time.time())}"
    
    print("\n" + "="*60)
    print("TEST 1: Create session with chat message")
    print("="*60)
    
    # Step 1: Send a chat message
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Create a bar chart: Q1=100, Q2=150, Q3=200",
            "session_id": session_id
        }
    )
    print(f"Chat response status: {response.status_code}")
    print(f"Response: {response.json().get('response', '')[:100]}")
    
    print_sessions("After chat message")
    
    print("\n" + "="*60)
    print("TEST 2: Upload Excel file to same session")
    print("="*60)
    
    # Step 2: Upload an Excel file (we'll use a simple test if file exists)
    excel_file = Path("backend/data/fdmg_timeseries_example.xlsx")
    if excel_file.exists():
        with open(excel_file, "rb") as f:
            files = {"file": (excel_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"session_id": session_id}
            response = requests.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )
        print(f"Upload response status: {response.status_code}")
        print(f"Response: {response.json().get('response', '')[:100]}")
    else:
        print("Excel file not found, skipping upload test")
    
    print_sessions("After Excel upload")
    
    print("\n" + "="*60)
    print("TEST 3: Delete session (new conversation)")
    print("="*60)
    
    # Step 3: Delete the session
    response = requests.delete(f"{BASE_URL}/api/chat/{session_id}")
    print(f"Delete response status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print_sessions("After session deletion")
    
    # Verify session is gone
    sessions = read_sessions()
    if session_id in sessions:
        print("\n❌ FAIL: Session still exists after deletion!")
    else:
        print("\n✅ PASS: Session successfully deleted!")

def test_multiple_sessions():
    """Test that multiple sessions can coexist"""
    print("\n" + "="*60)
    print("TEST 4: Multiple sessions coexist")
    print("="*60)
    
    session1 = f"test-session-1-{int(time.time())}"
    session2 = f"test-session-2-{int(time.time())}"
    
    # Create session 1
    requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "Session 1 message", "session_id": session1}
    )
    
    # Create session 2
    requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "Session 2 message", "session_id": session2}
    )
    
    print_sessions("After creating 2 sessions")
    
    # Delete session 1
    requests.delete(f"{BASE_URL}/api/chat/{session1}")
    
    print_sessions("After deleting session 1")
    
    # Verify only session 1 is deleted
    sessions = read_sessions()
    if session1 not in sessions and session2 in sessions:
        print("\n✅ PASS: Only target session deleted, other sessions intact!")
    else:
        print("\n❌ FAIL: Session deletion affected wrong sessions!")
    
    # Cleanup
    requests.delete(f"{BASE_URL}/api/chat/{session2}")

if __name__ == "__main__":
    try:
        print("Starting Session Management Tests...")
        print(f"Backend URL: {BASE_URL}")
        print(f"Session file: {SESSION_FILE}")
        
        # Initial state
        print_sessions("Initial state")
        
        # Run tests
        test_session_lifecycle()
        test_multiple_sessions()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
