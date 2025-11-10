"""Session and preference persistence service"""
import json
from datetime import datetime
from typing import Literal, Optional, List, Dict, Any
from pathlib import Path
from app.config.settings import settings


class PersistenceService:
    """Handles session storage and retrieval"""
    
    def __init__(self, session_file: Path = settings.SESSION_FILE):
        self.session_file = session_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the session file exists"""
        if not self.session_file.exists():
            self.session_file.write_text("{}")
    
    def _load_sessions(self) -> dict:
        """Load all sessions from file"""
        try:
            with open(self.session_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_sessions(self, sessions: dict):
        """Save all sessions to file"""
        with open(self.session_file, "w") as f:
            json.dump(sessions, f, indent=2)
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data by ID"""
        sessions = self._load_sessions()
        return sessions.get(session_id)
    
    def create_or_update_session(
        self, 
        session_id: str, 
        style: Literal["fd", "bnr"] = "fd"
    ) -> dict:
        """Create or update a session"""
        sessions = self._load_sessions()
        now = datetime.now().isoformat()
        
        if session_id in sessions:
            # Update existing session
            sessions[session_id]["style"] = style
            sessions[session_id]["last_used"] = now
        else:
            # Create new session
            sessions[session_id] = {
                "session_id": session_id,
                "style": style,
                "created_at": now,
                "last_used": now,
                "chat_history": []  # Initialize chat history
            }
        
        self._save_sessions(sessions)
        return sessions[session_id]
    
    def get_style_preference(self, session_id: str) -> Literal["fd", "bnr"]:
        """Get style preference for a session, default to 'fd'"""
        session = self.get_session(session_id)
        if session:
            return session.get("style", "fd")
        return "fd"
    
    def set_style_preference(
        self, 
        session_id: str, 
        style: Literal["fd", "bnr"]
    ) -> dict:
        """Set style preference for a session"""
        return self.create_or_update_session(session_id, style)
    
    def update_last_used(self, session_id: str):
        """Update the last_used timestamp for a session"""
        sessions = self._load_sessions()
        if session_id in sessions:
            sessions[session_id]["last_used"] = datetime.now().isoformat()
            self._save_sessions(sessions)
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        session = self.get_session(session_id)
        if session and "chat_history" in session:
            return session["chat_history"]
        return []
    
    def add_to_chat_history(
        self, 
        session_id: str, 
        role: Literal["user", "assistant", "system"], 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to chat history"""
        sessions = self._load_sessions()
        
        # Ensure session exists
        if session_id not in sessions:
            self.create_or_update_session(session_id)
            sessions = self._load_sessions()
        
        # Initialize chat_history if it doesn't exist
        if "chat_history" not in sessions[session_id]:
            sessions[session_id]["chat_history"] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            message["metadata"] = metadata
        
        sessions[session_id]["chat_history"].append(message)
        sessions[session_id]["last_used"] = datetime.now().isoformat()
        
        self._save_sessions(sessions)
    
    def clear_chat_history(self, session_id: str):
        """Clear chat history for a session"""
        sessions = self._load_sessions()
        if session_id in sessions:
            sessions[session_id]["chat_history"] = []
            self._save_sessions(sessions)


# Global instance
persistence = PersistenceService()
