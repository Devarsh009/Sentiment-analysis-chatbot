"""
Sentiment Analysis Service
============================
Wraps the ML inference pipeline for use by the API.
Provides a clean interface between the API layer and the ML model.
Includes a correction layer to catch common misclassifications
and a granular emotion detection layer.
"""

import re
import sys
import os
from typing import Dict

# Add ML directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "ml"))

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ─── Sentiment Override Patterns ─────────────────────────────────────────────

_STRONG_NEGATIVE_PATTERNS = [
    r"\b(fed up|sick of|tired of|had enough|can't stand|can't take)\b",
    r"\b(pissed|pissed off|furious|livid|enraged|fuming|seething)\b",
    r"\b(hate|hatred|loathe|detest|despise|abhor)\b",
    r"\b(miserable|depressed|devastated|heartbroken|hopeless|worthless)\b",
    r"\b(angry|mad|upset|frustrated|annoyed|irritated|agitated)\b",
    r"\b(terrible|horrible|awful|dreadful|disgusting|pathetic)\b",
    r"\b(i('?m| am) (so )?(sad|angry|mad|upset|unhappy|miserable|depressed|frustrated|furious|stressed|anxious|worried|scared|hurt|broken|lonely|exhausted))\b",
    r"\b(worst|sucks|suck|ruined|screwed|disaster|nightmare)\b",
    r"\b(cry|crying|cried|sobbing|tears)\b",
    r"\b(kill me|want to die|give up|no point|no hope)\b",
]

_STRONG_POSITIVE_PATTERNS = [
    r"\b(i('?m| am) (so )?(happy|excited|thrilled|grateful|thankful|blessed|delighted|overjoyed|ecstatic|proud|amazed|glad))\b",
    r"\b(love it|love this|loving|adore|amazing|wonderful|fantastic|incredible|brilliant|excellent|outstanding|magnificent|spectacular)\b",
    r"\b(best day|so happy|so excited|great news|can't wait|over the moon)\b",
    r"\b(thank you|thanks so much|appreciate|grateful)\b",
]

_COMPILED_NEGATIVE = [re.compile(p, re.IGNORECASE) for p in _STRONG_NEGATIVE_PATTERNS]
_COMPILED_POSITIVE = [re.compile(p, re.IGNORECASE) for p in _STRONG_POSITIVE_PATTERNS]


def _check_sentiment_override(text: str):
    """
    Check if the text matches strong sentiment patterns that should
    override the model prediction. Returns (sentiment, confidence) or None.
    """
    neg_matches = sum(1 for p in _COMPILED_NEGATIVE if p.search(text))
    pos_matches = sum(1 for p in _COMPILED_POSITIVE if p.search(text))

    if neg_matches > 0 and neg_matches >= pos_matches:
        return "negative", min(0.85 + neg_matches * 0.05, 0.99)
    if pos_matches > 0 and pos_matches > neg_matches:
        return "positive", min(0.85 + pos_matches * 0.05, 0.99)
    return None


# ─── Granular Emotion Detection ──────────────────────────────────────────────
# Maps base sentiment + text patterns → specific emotions.
# Priority-ordered: first match wins within each sentiment bucket.

_EMOTION_PATTERNS = {
    "negative": [
        ("angry", [
            r"\b(angry|mad|furious|livid|enraged|fuming|seething|rage|pissed|pissed off)\b",
            r"\b(hate|hatred|loathe|detest|despise|abhor)\b",
            r"\b(fed up|sick of|can't stand)\b",
        ]),
        ("frustrated", [
            r"\b(frustrated|frustrating|irritated|annoyed|agitated|exasperated)\b",
            r"\b(ugh|argh|ffs|so annoying|drives me crazy)\b",
            r"\b(tired of|had enough|nothing works|keeps failing)\b",
        ]),
        ("sad", [
            r"\b(sad|unhappy|depressed|miserable|heartbroken|devastated|grief|mourning)\b",
            r"\b(cry|crying|cried|sobbing|tears|weeping)\b",
            r"\b(lonely|alone|empty|hopeless|lost)\b",
        ]),
        ("worried", [
            r"\b(worried|anxious|nervous|scared|afraid|terrified|stressed|uneasy|dread)\b",
            r"\b(panic|panicking|freaking out|can't sleep|overthinking)\b",
            r"\b(what if|i('?m| am) (so )?scared|fear)\b",
        ]),
        ("disappointed", [
            r"\b(disappointed|let down|expected more|underwhelming|letdown)\b",
            r"\b(not what i|didn't live up|waste of|wasn't worth)\b",
        ]),
    ],
    "positive": [
        ("excited", [
            r"\b(excited|thrilled|ecstatic|stoked|pumped|hyped|can't wait|overjoyed)\b",
            r"\b(amazing|incredible|awesome|epic|insane|unreal|mind.?blowing)\b",
            r"\b(omg|oh my god|yes|yay|woohoo|woo|let's go)\b",
        ]),
        ("grateful", [
            r"\b(grateful|thankful|blessed|appreciate|thank you|thanks so much)\b",
            r"\b(means a lot|so kind|helped me|lifesaver|you're the best)\b",
        ]),
        ("happy", [
            r"\b(happy|glad|cheerful|delighted|pleased|joyful|content|wonderful)\b",
            r"\b(love it|love this|loving|adore|fantastic|great|perfect)\b",
            r"\b(good day|feeling good|life is good|so good)\b",
        ]),
        ("proud", [
            r"\b(proud|accomplished|achieved|nailed it|crushed it|did it|succeeded)\b",
            r"\b(finally|hard work paid off|milestone|breakthrough|personal best)\b",
        ]),
    ],
    "neutral": [
        ("curious", [
            r"\b(curious|wondering|how does|what is|why does|tell me|explain)\b",
            r"\b(question|interested|want to know|learn|understand)\b",
            r"\?",
        ]),
        ("confused", [
            r"\b(confused|confusing|don't understand|makes no sense|lost|huh|what)\b",
            r"\b(i('?m| am) (so )?confused|doesn't make sense|unclear)\b",
        ]),
        ("thoughtful", [
            r"\b(think|thinking|wonder|ponder|reflect|considering|maybe|perhaps)\b",
            r"\b(in my opinion|i believe|seems like|on one hand)\b",
        ]),
        ("normal", []),  # Default fallback for neutral
    ],
}

_COMPILED_EMOTIONS = {}
for _sentiment, _emotion_list in _EMOTION_PATTERNS.items():
    _COMPILED_EMOTIONS[_sentiment] = [
        (emotion, [re.compile(p, re.IGNORECASE) for p in patterns])
        for emotion, patterns in _emotion_list
    ]


def _detect_emotion(text: str, sentiment: str) -> str:
    """
    Detect granular emotion from text and base sentiment.
    Returns an emotion label like 'angry', 'excited', 'curious', etc.
    """
    emotion_list = _COMPILED_EMOTIONS.get(sentiment, [])
    for emotion, patterns in emotion_list:
        if not patterns:
            continue
        if any(p.search(text) for p in patterns):
            return emotion

    # Default emotions per sentiment
    defaults = {
        "negative": "sad",
        "positive": "happy",
        "neutral": "normal",
    }
    return defaults.get(sentiment, "normal")


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
        """Check if the model is loaded, trained, and ready for predictions."""
        return (SentimentService._predictor is not None and 
                SentimentService._predictor.is_loaded and
                SentimentService._predictor.is_trained)
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze the sentiment of a text message.
        
        Args:
            text: The input text to analyze
        
        Returns:
            Dictionary with sentiment, confidence, scores, and emotion
        """
        if not self.is_ready():
            logger.warning("Model not ready, returning default prediction")
            return self._fallback_prediction(text)
        
        try:
            result = SentimentService._predictor.predict(text)

            # Check if a strong sentiment override is needed
            override = _check_sentiment_override(text)
            if override and override[0] != result["sentiment"]:
                old = result["sentiment"]
                result["sentiment"] = override[0]
                result["confidence"] = round(override[1], 4)
                logger.info(
                    f"Sentiment override: '{text[:50]}' {old} → {override[0]}"
                )

            # Detect granular emotion
            result["emotion"] = _detect_emotion(text, result["sentiment"])

            logger.info(
                f"Prediction: '{text[:50]}...' → "
                f"{result['sentiment']} / {result['emotion']} ({result['confidence']:.2f})"
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
        
        emotion = _detect_emotion(text, sentiment)
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 4),
            "scores": {
                "negative": round(0.33 if sentiment != "negative" else confidence, 4),
                "neutral": round(0.34 if sentiment != "neutral" else confidence, 4),
                "positive": round(0.33 if sentiment != "positive" else confidence, 4),
            },
            "emotion": emotion,
            "fallback": True,
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if SentimentService._predictor:
            return SentimentService._predictor.get_model_info()
        return {"is_loaded": False, "error": "Predictor not initialized"}
