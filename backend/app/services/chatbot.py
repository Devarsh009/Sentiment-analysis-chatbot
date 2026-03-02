"""
Chatbot Response Service
=========================
Generates sentiment-aware chatbot responses.

Response Strategy:
    - NEGATIVE sentiment → Empathetic, supportive tone
    - POSITIVE sentiment → Enthusiastic, encouraging tone
    - NEUTRAL sentiment  → Standard informative tone
"""

import random
from typing import Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# RESPONSE TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════

POSITIVE_RESPONSES = [
    "That's wonderful to hear! 😊 Your positive energy is contagious! Is there anything else you'd like to chat about?",
    "I'm so glad you're feeling great! 🎉 It's always nice to hear good news. What else is on your mind?",
    "How fantastic! ✨ Your enthusiasm really brightens things up. Tell me more about what's making you happy!",
    "That's awesome! 🌟 I love your positive outlook. Keep that energy going! Anything else you'd like to share?",
    "What great news! 😄 It's wonderful when things go well. I'm here if you want to keep chatting!",
    "I can feel your excitement! 🙌 That's truly amazing. What other good things have been happening?",
    "How delightful! 💫 Your happiness is really coming through. I'd love to hear more about it!",
    "That sounds absolutely wonderful! 🎊 Keep spreading that positivity. What else can I help you with?",
]

NEGATIVE_RESPONSES = [
    "I'm sorry to hear you're going through that. 💙 I understand how frustrating that can be. Would you like to talk more about it?",
    "That sounds really tough, and I appreciate you sharing that with me. 🤗 Remember, it's okay to feel this way. How can I help?",
    "I hear you, and your feelings are completely valid. 💛 Things can be difficult sometimes. Is there anything specific I can help with?",
    "I'm sorry you're experiencing this. 🌿 Take a deep breath — it's okay to have challenging moments. I'm here to listen.",
    "That must be really hard. 💜 I want you to know that I'm here for you. Would you like to talk about what might help?",
    "I understand this is a difficult situation. 🫂 Sometimes just expressing how we feel can help. Tell me more if you'd like.",
    "I can sense this is weighing on you. 💙 Please know that your feelings matter. What would make things a little better?",
    "That's understandably upsetting. 🌷 I'm here to support you in any way I can. What's on your mind?",
]

NEUTRAL_RESPONSES = [
    "Thanks for your message! I'm here to help. Could you tell me more about what you're looking for?",
    "Got it! I'd be happy to assist you. What would you like to know more about?",
    "Thank you for reaching out! I'm here to help with whatever you need. What's on your mind?",
    "I understand. Let me know how I can assist you further. What questions do you have?",
    "Thanks for sharing that. I'm ready to help! Is there anything specific you'd like to discuss?",
    "Noted! I'm all ears. Feel free to ask me anything or share more details.",
    "I appreciate you reaching out! How can I make your experience better today?",
    "Sure thing! I'm here to help. What else would you like to talk about?",
]


class ChatbotService:
    """
    Service that generates chatbot responses based on detected sentiment.
    
    The chatbot adapts its tone and message style based on whether
    the user's message is positive, negative, or neutral.
    """
    
    def generate_response(self, message: str, sentiment: str, confidence: float) -> str:
        """
        Generate an appropriate chatbot response based on sentiment.
        
        Args:
            message: The original user message
            sentiment: Detected sentiment ('positive', 'negative', 'neutral')
            confidence: Confidence score of the prediction
        
        Returns:
            A string response tailored to the user's sentiment
        """
        logger.info(f"Generating response for sentiment: {sentiment} "
                    f"(confidence: {confidence:.2f})")
        
        if sentiment == "positive":
            response = random.choice(POSITIVE_RESPONSES)
        elif sentiment == "negative":
            response = random.choice(NEGATIVE_RESPONSES)
        else:
            response = random.choice(NEUTRAL_RESPONSES)
        
        # Add confidence context for very low confidence predictions
        if confidence < 0.5:
            response += (
                "\n\n_(I'm not entirely sure about the tone of your message. "
                "Feel free to let me know how you're really feeling!)_"
            )
        
        return response
    
    def generate_response_with_context(
        self, 
        message: str, 
        sentiment: str, 
        confidence: float,
        previous_sentiments: list = None,
    ) -> str:
        """
        Generate a response with conversation context awareness.
        
        If the user has been consistently negative, offer more support.
        If consistently positive, match their energy.
        
        Args:
            message: Current user message
            sentiment: Current detected sentiment
            confidence: Current prediction confidence
            previous_sentiments: List of previous sentiment labels
        
        Returns:
            Context-aware response string
        """
        response = self.generate_response(message, sentiment, confidence)
        
        # Check for persistent negative sentiment
        if previous_sentiments and len(previous_sentiments) >= 3:
            recent = previous_sentiments[-3:]
            if all(s == "negative" for s in recent):
                response += (
                    "\n\n💙 I've noticed you might be having a rough time. "
                    "Remember, it's completely okay to seek support. "
                    "If you need someone to talk to, don't hesitate to "
                    "reach out to friends, family, or a professional."
                )
                logger.info("Added persistent negative sentiment support message")
        
        return response
