"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings

# Create FastAPI app
app = FastAPI(
    title="AI Chart Generator",
    description="Generate charts from text or Excel using AI agents",
    version="1.0.0"
)

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
from app.api import routes
app.include_router(routes.router, prefix="/api", tags=["charts"])
