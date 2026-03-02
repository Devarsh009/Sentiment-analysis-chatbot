"""
Sentiment Analysis Service
============================
Wraps the ML inference pipeline for use by the API.
Provides a clean interface between the API layer and the ML model.
"""

import sys
import os
from typing import Dict

# Add ML directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "ml"))

from app.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentService:
    """
    Service class for sentiment analysis.
    
    Wraps the ML SentimentPredictor with logging, error handling,
    and a clean API for the route handlers.
    
    Uses singleton pattern (via the underlying predictor).
    """
    
    _predictor = None
    
    def __init__(self):
        """Initialize the sentiment service."""
        if SentimentService._predictor is None:
            self._load_predictor()
    
    def _load_predictor(self):
        """Load the ML predictor."""
        try:
            from inference import SentimentPredictor
            SentimentService._predictor = SentimentPredictor()
            logger.info("Sentiment predictor loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentiment predictor: {e}")
            SentimentService._predictor = None
    
    def is_ready(self) -> bool:
        """Check if the model is loaded and ready for predictions."""
        return (SentimentService._predictor is not None and 
                SentimentService._predictor.is_loaded)
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze the sentiment of a text message.
        
        Args:
            text: The input text to analyze
        
        Returns:
            Dictionary with sentiment, confidence, and scores
        """
        if not self.is_ready():
            logger.warning("Model not ready, returning default prediction")
            return self._fallback_prediction(text)
        
        try:
            result = SentimentService._predictor.predict(text)
            logger.info(
                f"Prediction: '{text[:50]}...' → "
                f"{result['sentiment']} ({result['confidence']:.2f})"
            )
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._fallback_prediction(text)
    
    def _fallback_prediction(self, text: str) -> Dict:
        """
        Simple rule-based fallback when the model isn't available.
        Uses basic keyword matching as a backup.
        """
        text_lower = text.lower()
        
        # Simple keyword-based sentiment detection
        positive_words = {
            "love", "great", "amazing", "wonderful", "fantastic", "excellent",
            "happy", "joy", "excited", "awesome", "good", "best", "beautiful",
            "perfect", "brilliant", "superb", "delighted", "pleased", "glad",
            "thankful", "grateful", "nice", "lovely"
        }
        negative_words = {
            "hate", "terrible", "awful", "horrible", "bad", "worst", "angry",
            "sad", "disappointed", "frustrated", "annoyed", "upset", "disgusted",
            "miserable", "pathetic", "dreadful", "poor", "ugly", "boring",
            "painful", "unhappy", "depressed", "furious"
        }
        
        words = set(text_lower.split())
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)
        
        if pos_count > neg_count:
            sentiment = "positive"
            confidence = min(0.6 + (pos_count * 0.1), 0.85)
        elif neg_count > pos_count:
            sentiment = "negative"
            confidence = min(0.6 + (neg_count * 0.1), 0.85)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 4),
            "scores": {
                "negative": round(0.33 if sentiment != "negative" else confidence, 4),
                "neutral": round(0.34 if sentiment != "neutral" else confidence, 4),
                "positive": round(0.33 if sentiment != "positive" else confidence, 4),
            },
            "fallback": True,
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if SentimentService._predictor:
            return SentimentService._predictor.get_model_info()
        return {"is_loaded": False, "error": "Predictor not initialized"}
