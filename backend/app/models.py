"""
Pydantic Models (Schemas)
==========================
Request and response schemas for the API endpoints.
Pydantic provides automatic validation, serialization, and documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════════════════

class PredictRequest(BaseModel):
    """Request body for the /predict endpoint."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The text message to analyze for sentiment",
        json_schema_extra={"example": "I love this product! It's amazing!"}
    )


class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message to the chatbot",
        json_schema_extra={"example": "I'm having a terrible day today."}
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for conversation tracking"
    )


class RetrainRequest(BaseModel):
    """Request body for admin retraining trigger."""
    min_confidence: float = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for training data"
    )
    epochs: int = Field(
        2,
        ge=1,
        le=10,
        description="Number of retraining epochs"
    )
    learning_rate: float = Field(
        1e-5,
        gt=0,
        description="Learning rate for retraining"
    )


# ═══════════════════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class SentimentScores(BaseModel):
    """Probability scores for each sentiment class."""
    negative: float = Field(..., description="Probability of negative sentiment")
    neutral: float = Field(..., description="Probability of neutral sentiment")
    positive: float = Field(..., description="Probability of positive sentiment")


class PredictResponse(BaseModel):
    """Response from the /predict endpoint."""
    sentiment: str = Field(
        ...,
        description="Detected sentiment: positive, negative, or neutral"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the prediction"
    )
    scores: Optional[SentimentScores] = Field(
        None,
        description="Probability scores for each sentiment class"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "sentiment": "positive",
                "confidence": 0.97,
                "scores": {
                    "negative": 0.01,
                    "neutral": 0.02,
                    "positive": 0.97
                }
            }]
        }
    }


class ChatResponse(BaseModel):
    """Response from the /chat endpoint."""
    reply: str = Field(..., description="Chatbot's response message")
    sentiment: str = Field(..., description="Detected sentiment of user's message")
    confidence: float = Field(..., description="Sentiment prediction confidence")
    session_id: Optional[str] = Field(None, description="Session ID")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Response timestamp"
    )


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""
    status: str = Field(..., description="Service health status")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
    version: str = Field(..., description="API version")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class AnalyticsResponse(BaseModel):
    """Response from the admin analytics endpoint."""
    total_messages: int = Field(..., description="Total messages processed")
    sentiment_distribution: Dict[str, int] = Field(
        ..., description="Count of each sentiment"
    )
    average_confidence: float = Field(
        ..., description="Average prediction confidence"
    )
    recent_messages: List[Dict] = Field(
        ..., description="Recent messages with details"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error info")
