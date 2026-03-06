"""
Inference Pipeline
===================
Production-ready inference module for sentiment prediction.

This module:
1. Loads the trained model once (singleton pattern)
2. Provides fast prediction on single texts or batches
3. Returns sentiment label + confidence score
4. Handles errors gracefully

Usage:
    from inference import SentimentPredictor
    
    predictor = SentimentPredictor()
    result = predictor.predict("I love this product!")
    # {'sentiment': 'positive', 'confidence': 0.97, 'scores': {...}}
"""

import os
import torch
import numpy as np
from typing import Dict, List, Optional, Union
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import (
    MODEL_OUTPUT_DIR, MODEL_NAME, LABEL_MAP,
    MAX_SEQ_LENGTH, CONFIDENCE_THRESHOLD, DEFAULT_SENTIMENT,
)


class SentimentPredictor:
    """
    Singleton sentiment prediction class.
    
    Loads the trained DistilBERT model and provides efficient inference.
    Uses GPU if available, falls back to CPU.
    
    Attributes:
        model: The loaded transformer model
        tokenizer: The tokenizer matching the model
        device: torch device (cuda/cpu)
        is_loaded: Whether the model has been loaded
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - only one model instance in memory."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_dir: str = MODEL_OUTPUT_DIR):
        """
        Initialize the predictor (only runs once due to singleton).
        
        Args:
            model_dir: Path to the trained model directory
        """
        if self._initialized:
            return
        
        self.model_dir = model_dir
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        self.is_trained = False
        self._initialized = True
        
        # Try to load the model
        self._load_model()
    
    def _load_model(self):
        """
        Load the trained model and tokenizer from disk.
        Falls back to the base pretrained model if no trained model exists.
        """
        try:
            if os.path.exists(self.model_dir):
                print(f"🧠 Loading trained model from {self.model_dir}...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_dir
                )
                self.is_trained = True
            else:
                print(f"⚠️  No trained model found. Using keyword-based analysis.")
                print(f"   Run 'python ml/train.py' to train a custom model.")
                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    MODEL_NAME,
                    num_labels=len(LABEL_MAP),
                    id2label=LABEL_MAP,
                    label2id={v: k for k, v in LABEL_MAP.items()},
                )
                self.is_trained = False
            
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            self.is_loaded = True
            
            print(f"✅ Model loaded on {self.device} "
                  f"({self.model.num_parameters():,} params)")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.is_loaded = False
    
    def predict(self, text: str) -> Dict:
        """
        Predict sentiment for a single text input.
        
        Args:
            text: The input text to analyze
        
        Returns:
            Dictionary with:
                - sentiment: str ('positive', 'negative', 'neutral')
                - confidence: float (0.0 to 1.0)  
                - scores: dict with probabilities for each class
        
        Example:
            >>> predictor.predict("I love this!")
            {
                'sentiment': 'positive',
                'confidence': 0.97,
                'scores': {'negative': 0.01, 'neutral': 0.02, 'positive': 0.97}
            }
        """
        if not self.is_loaded:
            return {
                "sentiment": DEFAULT_SENTIMENT,
                "confidence": 0.0,
                "scores": {label: 0.0 for label in LABEL_MAP.values()},
                "error": "Model not loaded"
            }
        
        try:
            # Tokenize the input text
            inputs = self.tokenizer(
                text,
                padding="max_length",
                truncation=True,
                max_length=MAX_SEQ_LENGTH,
                return_tensors="pt",  # Return PyTorch tensors
            )
            
            # Move to device (GPU/CPU)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference (no gradient computation needed)
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Convert logits to probabilities using softmax
            probabilities = torch.softmax(outputs.logits, dim=-1)
            probs_np = probabilities.cpu().numpy()[0]
            
            # Get predicted class and confidence
            predicted_class = int(np.argmax(probs_np))
            confidence = float(probs_np[predicted_class])
            
            # Map to label
            sentiment = LABEL_MAP.get(predicted_class, DEFAULT_SENTIMENT)
            
            # If confidence is below threshold, default to neutral
            if confidence < CONFIDENCE_THRESHOLD:
                sentiment = DEFAULT_SENTIMENT
            
            # Build scores dictionary
            scores = {
                LABEL_MAP[i]: float(probs_np[i])
                for i in range(len(probs_np))
            }
            
            return {
                "sentiment": sentiment,
                "confidence": round(confidence, 4),
                "scores": {k: round(v, 4) for k, v in scores.items()},
            }
            
        except Exception as e:
            return {
                "sentiment": DEFAULT_SENTIMENT,
                "confidence": 0.0,
                "scores": {label: 0.0 for label in LABEL_MAP.values()},
                "error": str(e),
            }
    
    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """
        Predict sentiment for multiple texts efficiently.
        
        Args:
            texts: List of input texts
        
        Returns:
            List of prediction dictionaries
        """
        if not self.is_loaded:
            return [self.predict(t) for t in texts]
        
        try:
            # Tokenize all texts at once
            inputs = self.tokenizer(
                texts,
                padding="max_length",
                truncation=True,
                max_length=MAX_SEQ_LENGTH,
                return_tensors="pt",
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probabilities = torch.softmax(outputs.logits, dim=-1)
            probs_np = probabilities.cpu().numpy()
            
            results = []
            for i in range(len(texts)):
                predicted_class = int(np.argmax(probs_np[i]))
                confidence = float(probs_np[i][predicted_class])
                sentiment = LABEL_MAP.get(predicted_class, DEFAULT_SENTIMENT)
                
                if confidence < CONFIDENCE_THRESHOLD:
                    sentiment = DEFAULT_SENTIMENT
                
                scores = {
                    LABEL_MAP[j]: float(probs_np[i][j])
                    for j in range(probs_np.shape[1])
                }
                
                results.append({
                    "sentiment": sentiment,
                    "confidence": round(confidence, 4),
                    "scores": {k: round(v, 4) for k, v in scores.items()},
                })
            
            return results
            
        except Exception as e:
            return [{
                "sentiment": DEFAULT_SENTIMENT,
                "confidence": 0.0,
                "scores": {label: 0.0 for label in LABEL_MAP.values()},
                "error": str(e),
            } for _ in texts]
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            "model_dir": self.model_dir,
            "is_loaded": self.is_loaded,
            "device": str(self.device),
            "parameters": self.model.num_parameters() if self.model else 0,
            "labels": LABEL_MAP,
        }


# ─── Quick Test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    predictor = SentimentPredictor()
    
    test_texts = [
        "I absolutely love this product! Best purchase ever!",
        "This is terrible, worst experience of my life.",
        "It's okay, nothing special about it.",
        "I'm so happy and excited about the news!",
        "Very disappointed and frustrated with the service.",
        "The weather is cloudy today.",
    ]
    
    print("\n" + "=" * 60)
    print("🧪 INFERENCE TEST")
    print("=" * 60)
    
    for text in test_texts:
        result = predictor.predict(text)
        print(f"\n📝 \"{text[:60]}...\"")
        print(f"   Sentiment:  {result['sentiment']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Scores:     {result['scores']}")
