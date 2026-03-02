"""
Retraining Script (Continuous Learning)
========================================
Enables continuous learning by retraining the model with new user data.

This script:
1. Loads previously collected user messages from the database
2. Combines them with original training data
3. Retrains the model incrementally
4. Saves the updated model

Usage:
    python retrain.py                          # Retrain with collected data
    python retrain.py --db-path ../backend/chatbot.db
    python retrain.py --epochs 2 --lr 1e-5     # Fine-tune gently
"""

import os
import sys
import argparse
import sqlite3
import pandas as pd
from datetime import datetime

from config import (
    MODEL_OUTPUT_DIR, EPOCHS, BATCH_SIZE, 
    LEARNING_RATE, REVERSE_LABEL_MAP,
)
from preprocess import load_custom_dataset, tokenize_dataset
from train import train_model


def extract_training_data_from_db(
    db_path: str,
    min_confidence: float = 0.7,
    output_csv: str = None,
) -> str:
    """
    Extract user messages from SQLite database for retraining.
    
    Only includes messages with confidence above the threshold,
    so we're training on relatively certain predictions.
    
    Args:
        db_path: Path to the SQLite database
        min_confidence: Minimum confidence to include a sample
        output_csv: Path to save the extracted CSV
    
    Returns:
        Path to the generated CSV file
    """
    print(f"📂 Extracting data from: {db_path}")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    # Query messages with their detected sentiments
    query = """
        SELECT message as text, sentiment as label, confidence
        FROM messages
        WHERE confidence >= ?
        AND sentiment IS NOT NULL
        ORDER BY timestamp DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(min_confidence,))
    conn.close()
    
    if len(df) == 0:
        print("⚠️  No qualifying data found in database.")
        return None
    
    # Keep only text and label columns
    df = df[["text", "label"]]
    
    # Save to CSV
    if output_csv is None:
        output_csv = os.path.join(
            os.path.dirname(db_path), 
            f"retrain_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    
    df.to_csv(output_csv, index=False)
    
    print(f"✅ Extracted {len(df)} samples")
    print(f"   Distribution: {df['label'].value_counts().to_dict()}")
    print(f"   Saved to: {output_csv}")
    
    return output_csv


def retrain_model(
    db_path: str = None,
    csv_path: str = None,
    epochs: int = 2,
    learning_rate: float = 1e-5,
    min_confidence: float = 0.7,
):
    """
    Retrain the model with new data (continuous learning).
    
    Uses a lower learning rate and fewer epochs to avoid catastrophic forgetting.
    
    Args:
        db_path: Path to SQLite database with user messages
        csv_path: Direct path to CSV file (alternative to db_path)
        epochs: Number of retraining epochs (keep low)
        learning_rate: Learning rate (keep low to preserve knowledge)
        min_confidence: Minimum confidence for DB extraction
    """
    print("=" * 60)
    print("🔄 MODEL RETRAINING (Continuous Learning)")
    print("=" * 60)
    
    # Get training data
    if csv_path and os.path.exists(csv_path):
        data_path = csv_path
    elif db_path:
        data_path = extract_training_data_from_db(db_path, min_confidence)
        if data_path is None:
            print("❌ No data available for retraining.")
            return
    else:
        print("❌ Please provide --db-path or --csv-path")
        return
    
    # Backup current model
    backup_dir = MODEL_OUTPUT_DIR + f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(MODEL_OUTPUT_DIR):
        import shutil
        shutil.copytree(MODEL_OUTPUT_DIR, backup_dir)
        print(f"💾 Model backed up to: {backup_dir}")
    
    # Retrain with lower learning rate
    print(f"\n🔥 Retraining with lr={learning_rate}, epochs={epochs}")
    
    train_model(
        custom_csv=data_path,
        epochs=epochs,
        learning_rate=learning_rate,
        output_dir=MODEL_OUTPUT_DIR,
    )
    
    print("\n✅ Retraining complete! Model updated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain model with new data")
    parser.add_argument("--db-path", type=str, 
                       default=os.path.join(os.path.dirname(__file__), 
                                           "..", "backend", "chatbot.db"),
                       help="Path to SQLite database")
    parser.add_argument("--csv-path", type=str, default=None,
                       help="Direct path to CSV training data")
    parser.add_argument("--epochs", type=int, default=2,
                       help="Retraining epochs (default: 2)")
    parser.add_argument("--lr", type=float, default=1e-5,
                       help="Learning rate (default: 1e-5, keep low)")
    parser.add_argument("--min-confidence", type=float, default=0.7,
                       help="Min confidence threshold for DB data")
    
    args = parser.parse_args()
    
    retrain_model(
        db_path=args.db_path,
        csv_path=args.csv_path,
        epochs=args.epochs,
        learning_rate=args.lr,
        min_confidence=args.min_confidence,
    )
