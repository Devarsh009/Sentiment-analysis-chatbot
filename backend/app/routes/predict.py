"""
Sentiment Prediction Route
=============================
POST /api/predict - Analyze sentiment of a text message.

Input:  { "message": "I love this product!" }
Output: { "sentiment": "positive", "confidence": 0.97, "scores": {...} }
"""

from fastapi import APIRouter, HTTPException
from app.models import PredictRequest, PredictResponse, ErrorResponse
from app.services.sentiment import SentimentService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        200: {"description": "Sentiment prediction result"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    summary="Analyze Sentiment",
    description="Analyze the sentiment of a text message. "
                "Returns positive, negative, or neutral with confidence score.",
)
async def predict_sentiment(request: PredictRequest):
    """
    Predict the sentiment of a user message.
    
    This endpoint:
    1. Receives a text message
    2. Passes it through the DistilBERT sentiment model
    3. Returns the predicted sentiment and confidence
    """
    try:
        # Validate input
        if not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        # Get sentiment prediction
        sentiment_service = SentimentService()
        result = sentiment_service.analyze(request.message)
        
        # Check for errors
        if "error" in result:
            logger.warning(f"Prediction warning: {result['error']}")
        
        # Build response
        return PredictResponse(
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            scores=result.get("scores"),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
