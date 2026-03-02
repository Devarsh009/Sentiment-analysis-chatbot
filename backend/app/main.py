"""
FastAPI Application Entry Point
=================================
Main application file that:
1. Creates the FastAPI app instance
2. Configures CORS middleware
3. Registers all route handlers
4. Sets up event handlers (startup/shutdown)
5. Initializes the ML model on startup

Run with:
    cd backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path so we can import ml modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "ml"))

from app.config import get_settings
from app.models import HealthResponse
from app.routes.predict import router as predict_router
from app.routes.chat import router as chat_router
from app.routes.admin import router as admin_router
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.utils.logger import setup_logger, get_logger
from app.services.sentiment import SentimentService
from app.services.database import DatabaseService


# ─── Settings & Logger ───────────────────────────────────────────────────────
settings = get_settings()
setup_logger(settings.LOG_LEVEL, settings.LOG_FILE)
logger = get_logger(__name__)


# ─── Lifespan (Startup & Shutdown) ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Code before 'yield' runs on startup, after 'yield' runs on shutdown.
    """
    # ── STARTUP ──
    logger.info("🚀 Starting Sentiment Chatbot API...")
    
    # Initialize database
    db = DatabaseService()
    db.initialize()
    logger.info("✅ Database initialized")
    
    # Initialize ML model (loads into memory)
    sentiment_service = SentimentService()
    model_loaded = sentiment_service.is_ready()
    
    if model_loaded:
        logger.info("✅ ML model loaded successfully")
    else:
        logger.warning("⚠️  ML model not loaded - using fallback responses")
    
    logger.info(f"✅ API ready at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📖 Docs at http://{settings.HOST}:{settings.PORT}/docs")
    
    yield  # Application is running
    
    # ── SHUTDOWN ──
    logger.info("🛑 Shutting down Sentiment Chatbot API...")
    db.close()
    logger.info("✅ Cleanup complete")


# ─── Create FastAPI App ──────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## AI-Powered Sentiment-Aware Chatbot API
    
    This API provides:
    - **Sentiment Analysis**: Analyze text sentiment (positive/negative/neutral)
    - **Smart Chat**: Chatbot that adapts responses based on detected sentiment
    - **Analytics**: Admin dashboard with usage statistics
    
    ### Endpoints:
    - `POST /api/predict` - Analyze sentiment of a message
    - `POST /api/chat` - Chat with the sentiment-aware bot
    - `GET /api/admin/analytics` - View usage analytics
    - `GET /health` - Health check
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─── Middleware ──────────────────────────────────────────────────────────────
# CORS - Allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW,
)


# ─── Routes ─────────────────────────────────────────────────────────────────
app.include_router(predict_router, prefix="/api", tags=["Sentiment Analysis"])
app.include_router(chat_router, prefix="/api", tags=["Chatbot"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


# ─── Root & Health Endpoints ────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns the status of the API and ML model.
    """
    sentiment_service = SentimentService()
    
    return HealthResponse(
        status="healthy",
        model_loaded=sentiment_service.is_ready(),
        version=settings.APP_VERSION,
    )
