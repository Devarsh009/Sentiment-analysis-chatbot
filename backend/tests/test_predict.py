"""
Unit Tests - Prediction Endpoint
===================================
Tests for the /api/predict endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestPredictEndpoint:
    """Tests for the sentiment prediction endpoint."""
    
    def test_predict_success(self):
        """Test successful sentiment prediction."""
        response = client.post(
            "/api/predict",
            json={"message": "I love this product! It's amazing!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert "confidence" in data
        assert data["sentiment"] in ["positive", "negative", "neutral"]
        assert 0 <= data["confidence"] <= 1
    
    def test_predict_negative_message(self):
        """Test prediction with negative text."""
        response = client.post(
            "/api/predict",
            json={"message": "This is terrible and I hate it."}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] in ["positive", "negative", "neutral"]
        assert "confidence" in data
    
    def test_predict_neutral_message(self):
        """Test prediction with neutral text."""
        response = client.post(
            "/api/predict",
            json={"message": "The weather is cloudy today."}
        )
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
    
    def test_predict_empty_message(self):
        """Test that empty messages are rejected."""
        response = client.post(
            "/api/predict",
            json={"message": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_predict_missing_message(self):
        """Test that missing message field is rejected."""
        response = client.post(
            "/api/predict",
            json={}
        )
        assert response.status_code == 422
    
    def test_predict_long_message(self):
        """Test handling of long messages."""
        long_text = "This is great! " * 200
        response = client.post(
            "/api/predict",
            json={"message": long_text}
        )
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
    
    def test_predict_has_scores(self):
        """Test that response includes sentiment scores."""
        response = client.post(
            "/api/predict",
            json={"message": "I feel wonderful today!"}
        )
        assert response.status_code == 200
        data = response.json()
        if data.get("scores"):
            assert "negative" in data["scores"]
            assert "neutral" in data["scores"]
            assert "positive" in data["scores"]
