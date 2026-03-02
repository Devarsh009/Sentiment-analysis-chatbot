"""
Unit Tests - Chat Endpoint
============================
Tests for the /api/chat endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestChatEndpoint:
    """Tests for the chatbot endpoint."""
    
    def test_chat_success(self):
        """Test successful chat interaction."""
        response = client.post(
            "/api/chat",
            json={"message": "Hello, how are you?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "sentiment" in data
        assert "confidence" in data
        assert "session_id" in data
        assert "timestamp" in data
    
    def test_chat_with_session_id(self):
        """Test chat with a provided session ID."""
        session_id = "test-session-123"
        response = client.post(
            "/api/chat",
            json={"message": "I'm happy!", "session_id": session_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
    
    def test_chat_generates_session_id(self):
        """Test that a session ID is generated when not provided."""
        response = client.post(
            "/api/chat",
            json={"message": "Hello!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] is not None
        assert len(data["session_id"]) > 0
    
    def test_chat_positive_sentiment(self):
        """Test that positive messages get appropriate responses."""
        response = client.post(
            "/api/chat",
            json={"message": "I love everything about this! So amazing!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["reply"]) > 0
    
    def test_chat_negative_sentiment(self):
        """Test that negative messages get empathetic responses."""
        response = client.post(
            "/api/chat",
            json={"message": "I'm very sad and disappointed today."}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["reply"]) > 0
    
    def test_chat_empty_message(self):
        """Test that empty messages are rejected."""
        response = client.post(
            "/api/chat",
            json={"message": ""}
        )
        assert response.status_code == 422


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check(self):
        """Test the health endpoint returns correct structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
