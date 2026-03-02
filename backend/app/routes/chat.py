"""
Chat Route
============
POST /api/chat - Chat with the sentiment-aware chatbot.

The chatbot:
1. Analyzes the sentiment of the user's message
2. Generates an appropriate response based on the sentiment
3. Stores the interaction in the database for analytics & retraining
"""

import uuid
from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse, ErrorResponse
from app.services.sentiment import SentimentService
from app.services.chatbot import ChatbotService
from app.services.database import DatabaseService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Chatbot response"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    summary="Chat with Bot",
    description="Send a message to the sentiment-aware chatbot. "
                "The bot detects your sentiment and responds accordingly.",
)
async def chat(request: ChatRequest):
    """
    Chat endpoint with sentiment-aware responses.
    
    Flow:
    1. Analyze sentiment of user message
    2. Get conversation history for context
    3. Generate appropriate chatbot response
    4. Store interaction in database
    5. Return response with sentiment info
    """
    try:
        # Validate input
        if not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # ── Step 1: Analyze Sentiment ──
        sentiment_service = SentimentService()
        analysis = sentiment_service.analyze(request.message)
        
        sentiment = analysis["sentiment"]
        confidence = analysis["confidence"]
        
        # ── Step 2: Get Conversation Context ──
        db = DatabaseService()
        previous_sentiments = db.get_session_sentiments(session_id)
        
        # ── Step 3: Generate Response ──
        chatbot = ChatbotService()
        reply = chatbot.generate_response_with_context(
            message=request.message,
            sentiment=sentiment,
            confidence=confidence,
            previous_sentiments=previous_sentiments,
        )
        
        # ── Step 4: Store Interaction ──
        db.save_message(
            message=request.message,
            sentiment=sentiment,
            confidence=confidence,
            bot_response=reply,
            session_id=session_id,
        )
        
        # ── Step 5: Return Response ──
        return ChatResponse(
            reply=reply,
            sentiment=sentiment,
            confidence=confidence,
            session_id=session_id,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
