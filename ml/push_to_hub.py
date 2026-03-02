"""
Push Model to HuggingFace Hub
===============================
Uploads the trained model to HuggingFace Model Hub for sharing.

Prerequisites:
    1. Create a HuggingFace account at https://huggingface.co
    2. Create an access token at https://huggingface.co/settings/tokens
    3. Login: huggingface-cli login

Usage:
    python push_to_hub.py --model-id your-username/sentiment-model
"""

import os
import argparse
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from huggingface_hub import HfApi, login

from config import MODEL_OUTPUT_DIR, HF_HUB_MODEL_ID


def push_model_to_hub(
    model_dir: str = MODEL_OUTPUT_DIR,
    model_id: str = HF_HUB_MODEL_ID,
    token: str = None,
):
    """
    Push the trained model and tokenizer to HuggingFace Hub.
    
    Args:
        model_dir: Local path to the trained model
        model_id: HuggingFace Hub model ID (e.g., 'username/model-name')
        token: HuggingFace API token (optional if already logged in)
    """
    print("=" * 60)
    print("☁️  PUSH MODEL TO HUGGINGFACE HUB")
    print("=" * 60)
    
    # Login if token provided
    if token:
        login(token=token)
        print("✅ Logged in to HuggingFace Hub")
    
    # Load model and tokenizer
    print(f"\n📂 Loading model from: {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    
    # Push to hub
    print(f"\n⬆️  Pushing to: {model_id}")
    
    model.push_to_hub(model_id, use_auth_token=True)
    tokenizer.push_to_hub(model_id, use_auth_token=True)
    
    print(f"\n✅ Model pushed successfully!")
    print(f"   URL: https://huggingface.co/{model_id}")
    print(f"\n💡 To use this model:")
    print(f'   from transformers import pipeline')
    print(f'   classifier = pipeline("sentiment-analysis", model="{model_id}")')
    print(f'   result = classifier("I love this!")')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push model to HuggingFace Hub")
    parser.add_argument("--model-dir", type=str, default=MODEL_OUTPUT_DIR,
                       help="Path to trained model")
    parser.add_argument("--model-id", type=str, default=HF_HUB_MODEL_ID,
                       help="HuggingFace Hub model ID")
    parser.add_argument("--token", type=str, default=None,
                       help="HuggingFace API token")
    
    args = parser.parse_args()
    
    push_model_to_hub(
        model_dir=args.model_dir,
        model_id=args.model_id,
        token=args.token,
    )
