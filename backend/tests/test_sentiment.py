"""
Unit Tests - Sentiment Service
=================================
Tests for the sentiment analysis service and chatbot response generation.
"""

import pytest
from app.services.sentiment import SentimentService
from app.services.chatbot import ChatbotService


class TestSentimentService:
    """Tests for the SentimentService class."""
    
    def test_service_initialization(self):
        """Test that the service initializes without error."""
        service = SentimentService()
        assert service is not None
    
    def test_analyze_returns_required_fields(self):
        """Test that analyze returns all required fields."""
        service = SentimentService()
        result = service.analyze("This is a test message.")
        
        assert "sentiment" in result
        assert "confidence" in result
        assert "scores" in result
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert 0 <= result["confidence"] <= 1
    
    def test_analyze_positive_text(self):
        """Test analysis of clearly positive text."""
        service = SentimentService()
        result = service.analyze("I love this! Amazing wonderful great!")
        assert result["sentiment"] in ["positive", "neutral"]
    
    def test_analyze_negative_text(self):
        """Test analysis of clearly negative text."""
        service = SentimentService()
        result = service.analyze("I hate this terrible horrible awful thing!")
        assert result["sentiment"] in ["negative", "neutral"]
    
    def test_fallback_prediction(self):
        """Test the fallback prediction method."""
        service = SentimentService()
        result = service._fallback_prediction("I love this!")
        
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0
    
    def test_fallback_negative(self):
        """Test fallback with negative text."""
        service = SentimentService()
        result = service._fallback_prediction("I hate this terrible thing!")
        
        assert result["sentiment"] == "negative"
    
    def test_fallback_neutral(self):
        """Test fallback with neutral text."""
        service = SentimentService()
        result = service._fallback_prediction("The event happens at 3pm.")
        
        assert result["sentiment"] == "neutral"


class TestChatbotService:
    """Tests for the ChatbotService class."""
    
    def test_generate_positive_response(self):
        """Test response generation for positive sentiment."""
        chatbot = ChatbotService()
        response = chatbot.generate_response(
            "I'm so happy!", "positive", 0.95
        )
        assert len(response) > 0
        assert isinstance(response, str)
    
    def test_generate_negative_response(self):
        """Test response generation for negative sentiment."""
        chatbot = ChatbotService()
        response = chatbot.generate_response(
            "I'm feeling terrible.", "negative", 0.90
        )
        assert len(response) > 0
    
    def test_generate_neutral_response(self):
        """Test response generation for neutral sentiment."""
        chatbot = ChatbotService()
        response = chatbot.generate_response(
            "What time is it?", "neutral", 0.80
        )
        assert len(response) > 0
    
    def test_low_confidence_adds_disclaimer(self):
        """Test that low confidence adds a disclaimer."""
        chatbot = ChatbotService()
        response = chatbot.generate_response(
            "Something...", "neutral", 0.3
        )
        assert "not entirely sure" in response.lower()
    
    def test_context_aware_persistent_negative(self):
        """Test context-aware response for persistent negative sentiment."""
        chatbot = ChatbotService()
        response = chatbot.generate_response_with_context(
            "I'm sad again",
            "negative",
            0.85,
            previous_sentiments=["negative", "negative", "negative"],
        )
        assert "rough time" in response.lower() or "support" in response.lower()
