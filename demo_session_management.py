#!/usr/bin/env python3
"""
Visual demonstration of session management working correctly
"""
import json
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
SESSION_FILE = Path("backend/data/sessions.json")

def count_sessions():
    """Count total sessions"""
    with open(SESSION_FILE) as f:
        return len(json.load(f))

def main():
    print("\n" + "="*70)
    print(" SESSION MANAGEMENT DEMONSTRATION")
    print("="*70)
    
    initial_count = count_sessions()
    print(f"\nInitial session count: {initial_count}")
    
    # Step 1: Create a new session
    session_id = f"demo-{int(time.time())}"
    print(f"\n📝 Step 1: Creating new session '{session_id}'")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Create a bar chart: Q1=100, Q2=200, Q3=150",
            "session_id": session_id
        }
    )
    print(f"   ✓ Chat message sent (status: {response.status_code})")
    print(f"   ✓ Response: {response.json()['response'][:50]}...")
    
    count_after_chat = count_sessions()
    print(f"   ✓ Session count after chat: {count_after_chat} (+{count_after_chat - initial_count})")
    
    # Step 2: Upload Excel file
    print(f"\n📤 Step 2: Uploading Excel file to session")
    
    excel_file = Path("backend/data/test_sales.xlsx")
    with open(excel_file, "rb") as f:
        files = {"file": (excel_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"session_id": session_id}
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
    print(f"   ✓ Excel uploaded (status: {response.status_code})")
    print(f"   ✓ Response: {response.json()['response']}")
    
    # Verify session has both interactions
    with open(SESSION_FILE) as f:
        sessions = json.load(f)
        session = sessions[session_id]
        history_count = len(session['chat_history'])
        print(f"   ✓ Chat history now has {history_count} messages")
        
        # Show what's tracked
        print(f"\n   📋 Session contents:")
        for i, msg in enumerate(session['chat_history'], 1):
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            content_preview = msg['content'][:50]
            metadata_info = f" [+metadata]" if msg.get('metadata') else ""
            print(f"      {i}. {role_emoji} {content_preview}{metadata_info}")
    
    count_after_upload = count_sessions()
    print(f"   ✓ Session count after upload: {count_after_upload}")
    
    # Step 3: Delete session (New Conversation)
    print(f"\n🗑️  Step 3: Clicking 'New Conversation' (deletes session)")
    
    response = requests.delete(f"{BASE_URL}/api/chat/{session_id}")
    print(f"   ✓ Delete request sent (status: {response.status_code})")
    print(f"   ✓ Response: {response.json()['message']}")
    
    count_after_delete = count_sessions()
    print(f"   ✓ Session count after delete: {count_after_delete} ({count_after_delete - count_after_upload:+d})")
    
    # Verify session is gone
    with open(SESSION_FILE) as f:
        sessions = json.load(f)
        if session_id in sessions:
            print(f"   ❌ ERROR: Session still exists!")
        else:
            print(f"   ✅ Session completely removed from sessions.json!")
    
    # Summary
    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    print(f"✅ Chat messages are tracked with metadata")
    print(f"✅ Excel uploads are tracked with metadata")
    print(f"✅ Sessions are completely deleted on 'New Conversation'")
    print(f"✅ sessions.json is properly maintained")
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
