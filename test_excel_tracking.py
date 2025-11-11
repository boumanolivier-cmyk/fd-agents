#!/usr/bin/env python3
"""
Test Excel upload tracking in session
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

def print_session_details(session_id):
    """Print detailed session info"""
    sessions = read_sessions()
    if session_id not in sessions:
        print(f"❌ Session {session_id} not found!")
        return
    
    session = sessions[session_id]
    print(f"\n{'='*60}")
    print(f"Session: {session_id}")
    print(f"{'='*60}")
    print(f"Created: {session['created_at']}")
    print(f"Style: {session['style']}")
    print(f"Total messages: {len(session.get('chat_history', []))}")
    print(f"\nChat History:")
    for i, msg in enumerate(session.get('chat_history', [])):
        print(f"\n{i+1}. [{msg['role'].upper()}] {msg['timestamp']}")
        print(f"   Content: {msg['content']}")
        if msg.get('metadata'):
            print(f"   Metadata:")
            for key, value in msg['metadata'].items():
                if isinstance(value, list) and len(value) > 5:
                    print(f"     - {key}: [{len(value)} items]")
                else:
                    print(f"     - {key}: {value}")

def test_excel_tracking():
    """Test that Excel uploads are properly tracked in session"""
    session_id = f"excel-test-{int(time.time())}"
    
    print("\n" + "="*60)
    print("TEST: Excel upload tracking in session")
    print("="*60)
    
    # Step 1: Send a chat message first
    print("\n1. Sending initial chat message...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Create a bar chart: A=10, B=20, C=30",
            "session_id": session_id
        }
    )
    print(f"   Status: {response.status_code}")
    
    print_session_details(session_id)
    
    # Step 2: Upload an Excel file
    print("\n2. Uploading Excel file...")
    excel_file = Path("backend/data/test_sales.xlsx")
    if not excel_file.exists():
        print(f"   ❌ Excel file not found: {excel_file}")
        return
    
    with open(excel_file, "rb") as f:
        files = {"file": (excel_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"session_id": session_id}
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json().get('response', '')}")
    
    print_session_details(session_id)
    
    # Step 3: Send another chat message
    print("\n3. Sending follow-up chat message...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Make it a line chart",
            "session_id": session_id
        }
    )
    print(f"   Status: {response.status_code}")
    
    print_session_details(session_id)
    
    # Verify the session has all interactions
    sessions = read_sessions()
    session = sessions.get(session_id)
    
    if not session:
        print("\n❌ FAIL: Session not found after interactions!")
        return
    
    history = session.get('chat_history', [])
    
    # Should have: user msg, assistant response, user upload, assistant response, user msg, assistant response
    expected_count = 6
    if len(history) != expected_count:
        print(f"\n⚠️  WARNING: Expected {expected_count} messages, got {len(history)}")
    
    # Check if Excel upload is tracked
    excel_upload_found = False
    for msg in history:
        if msg['role'] == 'user' and 'Uploaded Excel file' in msg['content']:
            excel_upload_found = True
            print(f"\n✅ Found Excel upload in history!")
            if msg.get('metadata'):
                print(f"   Metadata present: {list(msg['metadata'].keys())}")
            break
    
    if not excel_upload_found:
        print(f"\n❌ FAIL: Excel upload not found in session history!")
    else:
        print(f"\n✅ PASS: Excel upload properly tracked in session!")
    
    # Step 4: Test "New Conversation" - should delete entire session
    print("\n4. Testing 'New Conversation' (delete session)...")
    response = requests.delete(f"{BASE_URL}/api/chat/{session_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Verify session is completely gone
    sessions = read_sessions()
    if session_id in sessions:
        print(f"\n❌ FAIL: Session still exists after deletion!")
    else:
        print(f"\n✅ PASS: Session completely deleted (wiped from sessions.json)!")

if __name__ == "__main__":
    try:
        test_excel_tracking()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
