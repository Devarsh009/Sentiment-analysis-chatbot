"""
ML Configuration
=================
Central configuration for all ML training, evaluation, and inference settings.
Modify these values to customize model training behavior.
"""

import os

# ─── Model Settings ──────────────────────────────────────────────────────────
MODEL_NAME = "distilbert-base-uncased"       # HuggingFace pretrained model
NUM_LABELS = 3                                # positive, negative, neutral
LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}
REVERSE_LABEL_MAP = {"negative": 0, "neutral": 1, "positive": 2}

# ─── Training Hyperparameters ────────────────────────────────────────────────
EPOCHS = 3                                    # Number of training epochs
BATCH_SIZE = 16                               # Batch size for training
EVAL_BATCH_SIZE = 32                          # Batch size for evaluation
LEARNING_RATE = 2e-5                          # Learning rate (AdamW)
WEIGHT_DECAY = 0.01                           # Weight decay for regularization
WARMUP_STEPS = 500                            # Linear warmup steps
MAX_SEQ_LENGTH = 128                          # Max token sequence length
GRADIENT_ACCUMULATION_STEPS = 1               # Gradient accumulation

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_OUTPUT_DIR = os.path.join(BASE_DIR, "trained_model")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

# ─── Dataset Settings ────────────────────────────────────────────────────────
DATASET_NAME = "sst2"                        # HuggingFace dataset name
DATASET_CONFIG = None                         # Dataset configuration (if any)
TRAIN_SPLIT = "train"
VALIDATION_SPLIT = "validation"
TEST_SPLIT = "test"

# ─── HuggingFace Hub (Optional) ─────────────────────────────────────────────
HF_HUB_MODEL_ID = "your-username/sentiment-chatbot-model"
PUSH_TO_HUB = False                           # Set True to push after training

# ─── Inference Settings ─────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.5                    # Minimum confidence for prediction
DEFAULT_SENTIMENT = "neutral"                 # Fallback sentiment
