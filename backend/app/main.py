import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.database.session import engine
from app.database.base import Base
from app.core.exceptions import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.api import auth, uploads, analysis, dashboard, reports

# Configure standard console and file loggers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("app.main")

# Auto-create SQLAlchemy Database Tables on application load
try:
    logger.info("Initializing database schema validation/creation...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema tables validated/created successfully.")
except Exception as e:
    logger.error(f"Failed to auto-initialize database schema: {str(e)}. Ensure PostgreSQL is running.", exc_info=True)

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade REST API backend for the 'AI Augmented Pitch Analyser'. "
                "Exposes endpoints for User Authentication, File Uploading, "
                "OpenAI Whisper Audio Transcriptions, DSP librosa feature extraction, NLTK/TextBlob NLP "
                "analysis, VC-level Feedback generation, and Score aggregations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Apply CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply API Audit logging middleware
app.add_middleware(LoggingMiddleware)

# Apply Global custom exception mapping handlers
register_exception_handlers(app)

# Mount Routers under standard V1 prefix (/api)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(uploads.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health Check"])
def health_check():
    """Application level health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": "1.0.0"
    }
