"""Application settings and configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application
    ENV: str = os.getenv("ENV", "development")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CHARTS_DIR: Path = BASE_DIR / "charts"
    DATA_DIR: Path = BASE_DIR / "data"
    SESSION_FILE: Path = DATA_DIR / "sessions.json"
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Chart colors
    COLORS = {
        "fd": {
            "primary": "#379596",
            "content": "#191919",
            "background": "#ffeadb"
        },
        "bnr": {
            "primary": "#ffd200",
            "content": "#000",
            "background": "#fff"
        }
    }
    
    def __init__(self):
        # Ensure directories exist
        self.CHARTS_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
        
        # Initialize sessions file if it doesn't exist
        if not self.SESSION_FILE.exists():
            self.SESSION_FILE.write_text("{}")

settings = Settings()
