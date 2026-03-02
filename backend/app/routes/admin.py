"""
Admin Routes
===============
Admin endpoints for analytics and model management.

Endpoints:
- GET  /api/admin/analytics  - Get usage analytics
- GET  /api/admin/model-info - Get model information
- POST /api/admin/retrain    - Trigger model retraining
"""

from fastapi import APIRouter, HTTPException
from app.models import AnalyticsResponse, ErrorResponse, RetrainRequest
from app.services.sentiment import SentimentService
from app.services.database import DatabaseService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Get Analytics",
    description="Get usage analytics including message counts, "
                "sentiment distribution, and recent messages.",
)
async def get_analytics():
    """
    Retrieve analytics data for the admin dashboard.
    
    Returns:
    - Total messages processed
    - Sentiment distribution (positive/negative/neutral counts)
    - Average prediction confidence
    - Recent messages with sentiment info
    - Daily message counts
    """
    try:
        db = DatabaseService()
        analytics = db.get_analytics()
        
        return AnalyticsResponse(
            total_messages=analytics["total_messages"],
            sentiment_distribution=analytics["sentiment_distribution"],
            average_confidence=analytics["average_confidence"],
            recent_messages=analytics["recent_messages"],
        )
        
    except Exception as e:
        logger.error(f"Analytics endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )


@router.get(
    "/model-info",
    summary="Get Model Info",
    description="Get information about the currently loaded ML model.",
)
async def get_model_info():
    """Get information about the loaded sentiment model."""
    try:
        sentiment_service = SentimentService()
        return sentiment_service.get_model_info()
        
    except Exception as e:
        logger.error(f"Model info error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        )


@router.post(
    "/retrain",
    summary="Trigger Retraining",
    description="Trigger model retraining with collected user data.",
    responses={
        200: {"description": "Retraining initiated"},
        500: {"model": ErrorResponse, "description": "Retraining failed"},
    },
)
async def trigger_retrain(request: RetrainRequest):
    """
    Trigger model retraining with collected user data.
    
    This is a simplified endpoint. In production, you'd want to:
    1. Run this as a background task
    2. Add authentication
    3. Add progress tracking
    """
    try:
        logger.info(
            f"Retraining requested: epochs={request.epochs}, "
            f"lr={request.learning_rate}, min_conf={request.min_confidence}"
        )
        
        # In production, this should be a background task
        # For now, we return instructions
        return {
            "status": "acknowledged",
            "message": (
                "Retraining should be triggered via the CLI for safety. "
                "Run: python ml/retrain.py "
                f"--epochs {request.epochs} "
                f"--lr {request.learning_rate} "
                f"--min-confidence {request.min_confidence}"
            ),
            "params": {
                "epochs": request.epochs,
                "learning_rate": request.learning_rate,
                "min_confidence": request.min_confidence,
            }
        }
        
    except Exception as e:
        logger.error(f"Retrain endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Retraining failed: {str(e)}"
        )
