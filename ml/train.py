"""
Model Training Script
======================
Fine-tunes a DistilBERT model on sentiment data using HuggingFace Trainer API.

This script:
1. Loads and tokenizes the dataset (SST-2 or custom)
2. Initializes DistilBERT with a classification head
3. Configures training arguments (learning rate, epochs, etc.)
4. Trains using HuggingFace Trainer API
5. Saves the trained model and tokenizer locally
6. Optionally pushes to HuggingFace Hub

Usage:
    python train.py                          # Train on SST-2
    python train.py --custom data/custom.csv # Train on custom data
    python train.py --epochs 5 --lr 3e-5     # Custom hyperparameters
"""

import os
import sys
import argparse
import numpy as np
from datetime import datetime

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)

from config import (
    MODEL_NAME, NUM_LABELS, LABEL_MAP,
    EPOCHS, BATCH_SIZE, EVAL_BATCH_SIZE,
    LEARNING_RATE, WEIGHT_DECAY, WARMUP_STEPS,
    MODEL_OUTPUT_DIR, LOGS_DIR,
    GRADIENT_ACCUMULATION_STEPS, PUSH_TO_HUB,
    HF_HUB_MODEL_ID,
)
from preprocess import (
    load_huggingface_dataset,
    load_custom_dataset,
    tokenize_dataset,
)


def compute_metrics(eval_pred):
    """
    Compute evaluation metrics during training.
    
    Calculates accuracy, precision, recall, and F1 score.
    This function is called by the Trainer at each evaluation step.
    
    Args:
        eval_pred: Tuple of (predictions, labels) from the model
    
    Returns:
        Dictionary of metric names and values
    """
    predictions, labels = eval_pred
    
    # Get predicted class (argmax of logits)
    preds = np.argmax(predictions, axis=-1)
    
    # Calculate accuracy
    accuracy = (preds == labels).mean()
    
    # Calculate per-class metrics
    from sklearn.metrics import precision_recall_fscore_support
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="weighted", zero_division=0
    )
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def train_model(
    dataset_name: str = "sst2",
    custom_csv: str = None,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    output_dir: str = MODEL_OUTPUT_DIR,
    max_train_samples: int = None,
):
    """
    Main training function that fine-tunes DistilBERT for sentiment analysis.
    
    Steps:
        1. Load dataset (HuggingFace or custom CSV)
        2. Tokenize using AutoTokenizer
        3. Load pretrained DistilBERT model
        4. Configure TrainingArguments
        5. Initialize Trainer and train
        6. Save model and tokenizer
    
    Args:
        dataset_name: HuggingFace dataset name
        custom_csv: Path to custom CSV (overrides dataset_name)
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate for optimizer
        output_dir: Where to save the trained model
    """
    print("=" * 60)
    print(">> SENTIMENT MODEL TRAINING")
    print("=" * 60)
    print(f"   Model: {MODEL_NAME}")
    print(f"   Epochs: {epochs}")
    print(f"   Batch Size: {batch_size}")
    print(f"   Learning Rate: {learning_rate}")
    print(f"   Output: {output_dir}")
    print("=" * 60)
    
    # ─── Step 1: Load Dataset ────────────────────────────────────────────
    print("\n[Step 1] Loading Dataset...")
    if custom_csv:
        dataset = load_custom_dataset(custom_csv)
    else:
        dataset = load_huggingface_dataset(dataset_name)
    
    # ─── Step 2: Tokenize Dataset ────────────────────────────────────────
    print("\n[Step 2] Tokenizing Dataset...")
    tokenized_dataset = tokenize_dataset(dataset)
    
    # Optionally limit training samples for faster training on CPU
    if max_train_samples and max_train_samples < len(tokenized_dataset["train"]):
        print(f"   Using subset: {max_train_samples} train samples")
        tokenized_dataset["train"] = tokenized_dataset["train"].shuffle(seed=42).select(range(max_train_samples))
    
    # ─── Step 3: Load Pretrained Model ───────────────────────────────────
    print(f"\n[Step 3] Loading {MODEL_NAME} with {NUM_LABELS}-class head...")
    
    # AutoModelForSequenceClassification adds a classification head
    # on top of the pretrained transformer
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,         # 3 classes: neg, neu, pos
        id2label=LABEL_MAP,            # {0: 'negative', 1: 'neutral', ...}
        label2id={v: k for k, v in LABEL_MAP.items()},
    )
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    print(f"   Model loaded: {model.num_parameters():,} parameters")
    
    # ─── Step 4: Configure Training Arguments ────────────────────────────
    print("\n[Step 4] Configuring Training...")
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    training_args = TrainingArguments(
        # Output & Logging
        output_dir=output_dir,
        logging_dir=LOGS_DIR,
        logging_steps=100,
        logging_strategy="steps",
        
        # Training Settings
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        learning_rate=learning_rate,
        weight_decay=WEIGHT_DECAY,
        warmup_steps=WARMUP_STEPS,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        
        # Evaluation Settings
        eval_strategy="epoch",           # Evaluate after each epoch
        save_strategy="epoch",           # Save checkpoint each epoch
        load_best_model_at_end=True,     # Load best model when done
        metric_for_best_model="f1",      # Use F1 to pick best model
        greater_is_better=True,
        
        # Performance
        fp16=False,                      # Set True if GPU supports it
        dataloader_num_workers=0,        # Workers for data loading
        
        # Misc
        seed=42,
        report_to="none",               # Disable wandb/tensorboard
        
        # Hub (optional)
        push_to_hub=PUSH_TO_HUB,
        hub_model_id=HF_HUB_MODEL_ID if PUSH_TO_HUB else None,
    )
    
    # ─── Step 5: Initialize Trainer ──────────────────────────────────────
    print("\n[Step 5] Initializing Trainer...")
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        compute_metrics=compute_metrics,
        processing_class=tokenizer,
        callbacks=[
            EarlyStoppingCallback(early_stopping_patience=2),
        ],
    )
    
    # ─── Step 6: Train! ─────────────────────────────────────────────────
    print("\n[Step 6] Training Started!")
    print("-" * 40)
    
    start_time = datetime.now()
    train_result = trainer.train()
    end_time = datetime.now()
    
    training_time = end_time - start_time
    
    print("-" * 40)
    print(f"Training complete in {training_time}")
    print(f"   Final train loss: {train_result.training_loss:.4f}")
    
    # ─── Step 7: Evaluate ────────────────────────────────────────────────
    print("\n[Step 7] Final Evaluation...")
    eval_results = trainer.evaluate()
    
    print(f"   Eval Loss:      {eval_results['eval_loss']:.4f}")
    print(f"   Eval Accuracy:  {eval_results['eval_accuracy']:.4f}")
    print(f"   Eval Precision: {eval_results['eval_precision']:.4f}")
    print(f"   Eval Recall:    {eval_results['eval_recall']:.4f}")
    print(f"   Eval F1:        {eval_results['eval_f1']:.4f}")
    
    # ─── Step 8: Save Model ─────────────────────────────────────────────
    print(f"\n[Step 8] Saving model to {output_dir}...")
    
    # Save the model and tokenizer
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Save training metrics
    metrics_path = os.path.join(output_dir, "training_metrics.txt")
    with open(metrics_path, "w") as f:
        f.write(f"Training Date: {datetime.now().isoformat()}\n")
        f.write(f"Model: {MODEL_NAME}\n")
        f.write(f"Epochs: {epochs}\n")
        f.write(f"Batch Size: {batch_size}\n")
        f.write(f"Learning Rate: {learning_rate}\n")
        f.write(f"Training Time: {training_time}\n")
        f.write(f"Train Loss: {train_result.training_loss:.4f}\n")
        for key, value in eval_results.items():
            f.write(f"{key}: {value:.4f}\n")
    
    print(f"   Model saved successfully!")
    print(f"   Metrics saved to {metrics_path}")
    
    # ─── Step 9: Push to Hub (optional) ──────────────────────────────────
    if PUSH_TO_HUB:
        print(f"\n[Step 9] Pushing to HuggingFace Hub...")
        trainer.push_to_hub()
        print(f"   Model pushed to: {HF_HUB_MODEL_ID}")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    
    return trainer, eval_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train sentiment analysis model")
    parser.add_argument("--dataset", type=str, default="sst2",
                       help="HuggingFace dataset name (default: sst2)")
    parser.add_argument("--custom", type=str, default=None,
                       help="Path to custom CSV dataset")
    parser.add_argument("--epochs", type=int, default=EPOCHS,
                       help=f"Training epochs (default: {EPOCHS})")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE,
                       help=f"Batch size (default: {BATCH_SIZE})")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE,
                       help=f"Learning rate (default: {LEARNING_RATE})")
    parser.add_argument("--output", type=str, default=MODEL_OUTPUT_DIR,
                       help=f"Output directory (default: {MODEL_OUTPUT_DIR})")
    parser.add_argument("--max-samples", type=int, default=None,
                       help="Max training samples (for faster CPU training)")
    
    args = parser.parse_args()
    
    train_model(
        dataset_name=args.dataset,
        custom_csv=args.custom,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        output_dir=args.output,
        max_train_samples=args.max_samples,
    )
