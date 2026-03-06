"""
Dataset Preprocessing Script
==============================
This script handles:
1. Loading datasets from HuggingFace datasets library
2. Tokenizing text using AutoTokenizer
3. Mapping labels to our 3-class system (negative/neutral/positive)
4. Supporting custom CSV datasets
5. Saving preprocessed data for training

Usage:
    python preprocess.py                    # Use default SST-2 dataset
    python preprocess.py --custom data.csv  # Use custom CSV dataset
"""

import os
import sys
import argparse
import pandas as pd
from datasets import load_dataset, Dataset, DatasetDict, ClassLabel, Features, Value
from transformers import AutoTokenizer
from config import (
    MODEL_NAME, MAX_SEQ_LENGTH, DATA_DIR,
    DATASET_NAME, REVERSE_LABEL_MAP
)


def load_huggingface_dataset(dataset_name: str = DATASET_NAME) -> DatasetDict:
    """
    Load a sentiment dataset from HuggingFace's datasets library.
    
    SST-2 (Stanford Sentiment Treebank) has binary labels:
        0 = negative, 1 = positive
    We map these to our 3-class system (neutral is added for edge cases).
    
    Args:
        dataset_name: Name of the HuggingFace dataset to load
    
    Returns:
        DatasetDict with train and validation splits
    """
    print(f"📦 Loading dataset: {dataset_name} from HuggingFace...")
    
    if dataset_name == "sst2":
        # Load SST-2 from GLUE benchmark
        dataset = load_dataset("glue", "sst2")
        
        # SST-2 has binary labels (0=negative, 1=positive)
        # We remap: 0 → 0 (negative), 1 → 2 (positive)
        def remap_sst2_labels(example):
            if example["label"] == 0:
                example["label"] = 0   # negative
            else:
                example["label"] = 2   # positive
            return example
        
        # Cast label column to plain int to avoid ClassLabel num_classes conflict
        for split in dataset:
            dataset[split] = dataset[split].cast_column("label", Value("int64"))
        
        dataset = dataset.map(remap_sst2_labels)
        
        # Rename 'sentence' column to 'text' for consistency
        dataset = dataset.rename_column("sentence", "text")
        
        print(f"✅ Loaded SST-2: {len(dataset['train'])} train, "
              f"{len(dataset['validation'])} validation samples")
        
    elif dataset_name == "imdb":
        # Load IMDb dataset (binary: neg=0, pos=1)
        dataset = load_dataset("imdb")
        
        def remap_imdb_labels(example):
            if example["label"] == 0:
                example["label"] = 0   # negative
            else:
                example["label"] = 2   # positive
            return example
        
        # Cast label column to plain int to avoid ClassLabel num_classes conflict
        for split in dataset:
            dataset[split] = dataset[split].cast_column("label", Value("int64"))
        
        dataset = dataset.map(remap_imdb_labels)
        
        # IMDb uses 'test' split, rename to 'validation' for consistency
        if "validation" not in dataset:
            dataset["validation"] = dataset["test"]
        
        print(f"✅ Loaded IMDb: {len(dataset['train'])} train, "
              f"{len(dataset['validation'])} validation samples")
    else:
        # Generic dataset loading
        dataset = load_dataset(dataset_name)
        print(f"✅ Loaded {dataset_name}")
    
    return dataset


def load_custom_dataset(csv_path: str) -> DatasetDict:
    """
    Load a custom CSV dataset for training.
    
    Expected CSV format:
        text,label
        "I love this product!",positive
        "Terrible experience.",negative
        "It was okay.",neutral
    
    Args:
        csv_path: Path to the CSV file
    
    Returns:
        DatasetDict with train and validation splits
    """
    print(f"📂 Loading custom dataset from: {csv_path}")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Validate required columns
    required_cols = {"text", "label"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must have columns: {required_cols}. "
                        f"Found: {set(df.columns)}")
    
    # Map string labels to integers
    if df["label"].dtype == object:
        df["label"] = df["label"].map(REVERSE_LABEL_MAP)
        if df["label"].isnull().any():
            invalid = df[df["label"].isnull()]["label"].unique()
            raise ValueError(f"Invalid labels found: {invalid}. "
                           f"Expected: {list(REVERSE_LABEL_MAP.keys())}")
    
    # Split into train (80%) and validation (20%)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    split_idx = int(len(df) * 0.8)
    
    train_df = df[:split_idx]
    val_df = df[split_idx:]
    
    dataset = DatasetDict({
        "train": Dataset.from_pandas(train_df, preserve_index=False),
        "validation": Dataset.from_pandas(val_df, preserve_index=False),
    })
    
    print(f"✅ Custom dataset loaded: {len(train_df)} train, "
          f"{len(val_df)} validation samples")
    
    return dataset


def tokenize_dataset(dataset: DatasetDict, model_name: str = MODEL_NAME) -> DatasetDict:
    """
    Tokenize the dataset using HuggingFace AutoTokenizer.
    
    This converts raw text into token IDs that the model can understand.
    Uses padding and truncation to ensure uniform sequence lengths.
    
    Args:
        dataset: DatasetDict with 'text' column
        model_name: HuggingFace model name for tokenizer
    
    Returns:
        Tokenized DatasetDict ready for training
    """
    print(f"🔤 Tokenizing with {model_name} tokenizer...")
    
    # Load the tokenizer matching our model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_function(examples):
        """Tokenize a batch of examples."""
        return tokenizer(
            examples["text"],
            padding="max_length",        # Pad to max_length
            truncation=True,             # Truncate if longer than max_length
            max_length=MAX_SEQ_LENGTH,   # Maximum sequence length
            return_tensors=None,         # Return as lists (for datasets)
        )
    
    # Apply tokenization to all splits
    tokenized = dataset.map(
        tokenize_function,
        batched=True,                    # Process in batches (faster)
        desc="Tokenizing",
    )
    
    # Remove the raw text column (model doesn't need it)
    if "text" in tokenized["train"].column_names:
        tokenized = tokenized.remove_columns(["text"])
    
    # Remove any extra columns that might cause issues
    extra_cols = [c for c in tokenized["train"].column_names 
                  if c not in ["input_ids", "attention_mask", "label"]]
    if extra_cols:
        tokenized = tokenized.remove_columns(extra_cols)
    
    # Set format for PyTorch
    tokenized.set_format("torch")
    
    print(f"✅ Tokenization complete! Columns: {tokenized['train'].column_names}")
    
    return tokenized


def create_sample_custom_dataset():
    """
    Create a sample custom CSV dataset for demonstration.
    This shows users the expected format for custom data.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    sample_data = [
        ("I absolutely love this product! Best purchase ever!", "positive"),
        ("This is amazing, I'm so happy with the results!", "positive"),
        ("Great experience, would highly recommend to everyone.", "positive"),
        ("The service was excellent and the staff was friendly.", "positive"),
        ("What a wonderful day, everything went perfectly!", "positive"),
        ("I'm thrilled with how this turned out.", "positive"),
        ("Fantastic quality, exceeded my expectations.", "positive"),
        ("This is the worst product I've ever bought.", "negative"),
        ("Terrible customer service, very disappointed.", "negative"),
        ("I regret this purchase, complete waste of money.", "negative"),
        ("The quality is awful and it broke after one day.", "negative"),
        ("Very frustrating experience, would not recommend.", "negative"),
        ("I'm really unhappy with this, it's garbage.", "negative"),
        ("Horrible, just horrible. Never buying again.", "negative"),
        ("It's okay, nothing special about it.", "neutral"),
        ("The product works as described, meets expectations.", "neutral"),
        ("Average experience, neither good nor bad.", "neutral"),
        ("It does what it's supposed to do.", "neutral"),
        ("Standard quality, nothing to complain about.", "neutral"),
        ("It's fine, serves its purpose adequately.", "neutral"),
    ]
    
    df = pd.DataFrame(sample_data, columns=["text", "label"])
    csv_path = os.path.join(DATA_DIR, "sample_dataset.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"📝 Sample dataset created at: {csv_path}")
    print(f"   Total samples: {len(df)}")
    print(f"   Labels: {df['label'].value_counts().to_dict()}")
    
    return csv_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess datasets for sentiment analysis")
    parser.add_argument("--custom", type=str, help="Path to custom CSV dataset")
    parser.add_argument("--dataset", type=str, default=DATASET_NAME,
                       help="HuggingFace dataset name (default: sst2)")
    parser.add_argument("--create-sample", action="store_true",
                       help="Create a sample custom CSV dataset")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_custom_dataset()
    elif args.custom:
        dataset = load_custom_dataset(args.custom)
        tokenized = tokenize_dataset(dataset)
        print(f"\n🎉 Preprocessing complete!")
        print(f"   Train samples: {len(tokenized['train'])}")
        print(f"   Validation samples: {len(tokenized['validation'])}")
    else:
        dataset = load_huggingface_dataset(args.dataset)
        tokenized = tokenize_dataset(dataset)
        print(f"\n🎉 Preprocessing complete!")
        print(f"   Train samples: {len(tokenized['train'])}")
        print(f"   Validation samples: {len(tokenized['validation'])}")
