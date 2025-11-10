"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.config.logging import setup_logging, get_logger

# Setup logging
setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Chart Generator",
    description="Generate charts from text or Excel using AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info("Starting AI Chart Generator application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving charts
app.mount("/charts", StaticFiles(directory=str(settings.CHARTS_DIR)), name="charts")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Chart Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routes
from app.api.routes import api_router
app.include_router(api_router, prefix="/api")
