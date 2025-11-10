"""Application settings and configuration"""
from pathlib import Path
from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables with Pydantic validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # API Keys
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for AI agent")
    
    # Application
    ENV: str = Field(default="development", description="Environment (development/production)")
    BACKEND_PORT: int = Field(default=8000, description="Backend server port")
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend URL for CORS")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    CHARTS_DIR: Path = Field(default=None, description="Directory for generated charts")
    DATA_DIR: Path = Field(default=None, description="Directory for data storage")
    SESSION_FILE: Path = Field(default=None, description="Session data file path")
    
    # CORS
    ALLOWED_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        description="Allowed CORS origins"
    )
    
    # Chart colors
    COLORS: Dict[str, Dict[str, str]] = Field(
        default={
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
        },
        description="Chart color schemes for FD and BNR styles"
    )
    
    @field_validator("CHARTS_DIR", mode="before")
    @classmethod
    def set_charts_dir(cls, v: Path | None, info) -> Path:
        """Set CHARTS_DIR relative to BASE_DIR if not provided"""
        if v is None:
            base_dir = info.data.get("BASE_DIR", Path(__file__).parent.parent.parent)
            return base_dir / "charts"
        return v
    
    @field_validator("DATA_DIR", mode="before")
    @classmethod
    def set_data_dir(cls, v: Path | None, info) -> Path:
        """Set DATA_DIR relative to BASE_DIR if not provided"""
        if v is None:
            base_dir = info.data.get("BASE_DIR", Path(__file__).parent.parent.parent)
            return base_dir / "data"
        return v
    
    @field_validator("SESSION_FILE", mode="before")
    @classmethod
    def set_session_file(cls, v: Path | None, info) -> Path:
        """Set SESSION_FILE relative to DATA_DIR if not provided"""
        if v is None:
            data_dir = info.data.get("DATA_DIR")
            if data_dir is None:
                base_dir = info.data.get("BASE_DIR", Path(__file__).parent.parent.parent)
                data_dir = base_dir / "data"
            return data_dir / "sessions.json"
        return v
    
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.CHARTS_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
        
        # Initialize sessions file if it doesn't exist
        if not self.SESSION_FILE.exists():
            self.SESSION_FILE.write_text("{}")

settings = Settings()
