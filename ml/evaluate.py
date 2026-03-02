"""
Model Evaluation Script
========================
Evaluates the trained sentiment model on test/validation data.

Generates:
- Classification report (precision, recall, F1 per class)
- Confusion matrix
- Sample predictions with confidence scores
- Overall accuracy

Usage:
    python evaluate.py                           # Evaluate on SST-2 validation
    python evaluate.py --custom data/test.csv    # Evaluate on custom data
    python evaluate.py --model-dir ./my_model    # Use specific model
"""

import os
import sys
import argparse
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix

from config import MODEL_OUTPUT_DIR, LABEL_MAP, NUM_LABELS, MAX_SEQ_LENGTH
from preprocess import load_huggingface_dataset, load_custom_dataset, tokenize_dataset


def load_trained_model(model_dir: str = MODEL_OUTPUT_DIR):
    """
    Load the trained model and tokenizer from disk.
    
    Args:
        model_dir: Path to the saved model directory
    
    Returns:
        Tuple of (model, tokenizer)
    """
    print(f"📂 Loading model from: {model_dir}")
    
    if not os.path.exists(model_dir):
        raise FileNotFoundError(
            f"Model not found at {model_dir}. "
            "Please run train.py first!"
        )
    
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()  # Set to evaluation mode
    
    print(f"✅ Model loaded: {model.num_parameters():,} parameters")
    return model, tokenizer


def evaluate_model(
    model_dir: str = MODEL_OUTPUT_DIR,
    dataset_name: str = "sst2",
    custom_csv: str = None,
    num_samples: int = 10,
):
    """
    Run complete evaluation on the trained model.
    
    Args:
        model_dir: Path to trained model
        dataset_name: HuggingFace dataset name
        custom_csv: Path to custom CSV test set
        num_samples: Number of sample predictions to show
    """
    print("=" * 60)
    print("📊 MODEL EVALUATION")
    print("=" * 60)
    
    # Load model
    model, tokenizer = load_trained_model(model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"   Device: {device}")
    
    # Load dataset
    print("\n📦 Loading evaluation dataset...")
    if custom_csv:
        dataset = load_custom_dataset(custom_csv)
    else:
        dataset = load_huggingface_dataset(dataset_name)
    
    # Get the raw text before tokenizing (for sample predictions)
    eval_split = dataset["validation"]
    raw_texts = eval_split["text"]
    true_labels = eval_split["label"]
    
    # Tokenize
    tokenized = tokenize_dataset(dataset)
    eval_dataset = tokenized["validation"]
    
    # ─── Run Predictions ─────────────────────────────────────────────────
    print("\n🔮 Running predictions...")
    
    all_preds = []
    all_probs = []
    
    # Process in batches
    batch_size = 32
    for i in range(0, len(eval_dataset), batch_size):
        batch_input_ids = eval_dataset[i:i+batch_size]["input_ids"].to(device)
        batch_attention = eval_dataset[i:i+batch_size]["attention_mask"].to(device)
        
        with torch.no_grad():
            outputs = model(
                input_ids=batch_input_ids,
                attention_mask=batch_attention,
            )
        
        probs = torch.softmax(outputs.logits, dim=-1)
        preds = torch.argmax(probs, dim=-1)
        
        all_preds.extend(preds.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)
    true_labels_array = np.array(true_labels)
    
    # ─── Classification Report ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("📋 CLASSIFICATION REPORT")
    print("=" * 60)
    
    # Get labels that actually appear in the data
    present_labels = sorted(set(true_labels_array) | set(all_preds))
    target_names = [LABEL_MAP[l] for l in present_labels]
    
    report = classification_report(
        true_labels_array, all_preds,
        labels=present_labels,
        target_names=target_names,
        digits=4,
    )
    print(report)
    
    # ─── Confusion Matrix ────────────────────────────────────────────────
    print("=" * 60)
    print("🔢 CONFUSION MATRIX")
    print("=" * 60)
    
    cm = confusion_matrix(true_labels_array, all_preds, labels=present_labels)
    
    # Pretty print
    header = "  Predicted →  " + "  ".join(f"{LABEL_MAP[l]:>8}" for l in present_labels)
    print(header)
    print("  " + "-" * len(header))
    for i, label in enumerate(present_labels):
        row = f"  {LABEL_MAP[label]:>10} |  " + "  ".join(f"{cm[i][j]:>8}" for j in range(len(present_labels)))
        print(row)
    
    # ─── Overall Accuracy ────────────────────────────────────────────────
    accuracy = (all_preds == true_labels_array).mean()
    print(f"\n📈 Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # ─── Sample Predictions ──────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"🔍 SAMPLE PREDICTIONS (showing {num_samples})")
    print(f"{'=' * 60}")
    
    # Pick random samples
    indices = np.random.choice(len(raw_texts), min(num_samples, len(raw_texts)), replace=False)
    
    for idx in indices:
        text = raw_texts[idx][:80] + ("..." if len(raw_texts[idx]) > 80 else "")
        true_label = LABEL_MAP[true_labels_array[idx]]
        pred_label = LABEL_MAP[all_preds[idx]]
        confidence = all_probs[idx].max()
        
        status = "✅" if true_label == pred_label else "❌"
        
        print(f"\n  {status} Text: \"{text}\"")
        print(f"     True: {true_label:>10}  |  Pred: {pred_label:>10}  |  "
              f"Confidence: {confidence:.4f}")
    
    # ─── Confidence Distribution ─────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("📊 CONFIDENCE DISTRIBUTION")
    print(f"{'=' * 60}")
    
    max_probs = all_probs.max(axis=1)
    print(f"   Mean confidence:   {max_probs.mean():.4f}")
    print(f"   Median confidence: {np.median(max_probs):.4f}")
    print(f"   Min confidence:    {max_probs.min():.4f}")
    print(f"   Max confidence:    {max_probs.max():.4f}")
    
    # Confidence buckets
    for threshold in [0.9, 0.8, 0.7, 0.6, 0.5]:
        count = (max_probs >= threshold).sum()
        pct = count / len(max_probs) * 100
        print(f"   ≥ {threshold}: {count:>6} samples ({pct:.1f}%)")
    
    print(f"\n{'=' * 60}")
    print("🎉 EVALUATION COMPLETE!")
    print(f"{'=' * 60}")
    
    return {
        "accuracy": accuracy,
        "predictions": all_preds,
        "probabilities": all_probs,
        "classification_report": report,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate sentiment model")
    parser.add_argument("--model-dir", type=str, default=MODEL_OUTPUT_DIR,
                       help="Path to trained model directory")
    parser.add_argument("--dataset", type=str, default="sst2",
                       help="HuggingFace dataset name")
    parser.add_argument("--custom", type=str, default=None,
                       help="Path to custom CSV test dataset")
    parser.add_argument("--samples", type=int, default=10,
                       help="Number of sample predictions to display")
    
    args = parser.parse_args()
    
    evaluate_model(
        model_dir=args.model_dir,
        dataset_name=args.dataset,
        custom_csv=args.custom,
        num_samples=args.samples,
    )
