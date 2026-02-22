"""
Model training script for the Intelligent Digital Fraud Awareness and Detection Platform.

This script trains a fraud detection model using TF-IDF vectorization and Logistic Regression.
The trained model and vectorizer are saved as pickle files for offline inference.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle
from pathlib import Path
import sys


def train_model(data_path: str, output_dir: str = "backend/models/"):
    """
    Trains fraud detection model and saves artifacts.
    
    Steps:
    1. Load CSV data with "text" and "label" columns
    2. Validate minimum 100 samples
    3. Split into train/validation sets (80/20) with stratification
    4. Create TF-IDF vectorizer (max_features=5000, ngram_range=(1, 2))
    5. Train Logistic Regression classifier (max_iter=1000)
    6. Evaluate on validation set
    7. Save model and vectorizer to pickle files
    
    Args:
        data_path: Path to training CSV file with "text" and "label" columns
        output_dir: Directory to save model artifacts (default: backend/models/)
    
    Returns:
        dict: Training metrics (accuracy, precision, recall, f1)
    
    Raises:
        ValueError: If training data is insufficient (< 100 samples)
        FileNotFoundError: If data_path does not exist
    """
    print(f"Loading training data from {data_path}...")
    
    # Load data
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Training data file not found: {data_path}")
    
    # Validate required columns
    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError("CSV must contain 'text' and 'label' columns")
    
    # Validate minimum samples
    if len(df) < 100:
        raise ValueError(f"Insufficient training data: {len(df)} samples (minimum 100 required)")
    
    print(f"Loaded {len(df)} samples")
    print(f"Class distribution: {df['label'].value_counts().to_dict()}")
    
    X = df['text']
    y = df['label']
    
    # Split data with stratification
    print("\nSplitting data into train/validation sets (80/20)...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    # Vectorization
    print("\nCreating TF-IDF vectorizer (max_features=5000, ngram_range=(1, 2))...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
    
    # Train model
    print("\nTraining Logistic Regression classifier (max_iter=1000)...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_vec, y_train)
    
    print("Training complete!")
    
    # Evaluate
    print("\nEvaluating on validation set...")
    y_pred = model.predict(X_val_vec)
    
    metrics = {
        'accuracy': accuracy_score(y_val, y_pred),
        'precision': precision_score(y_val, y_pred),
        'recall': recall_score(y_val, y_pred),
        'f1': f1_score(y_val, y_pred)
    }
    
    print("\n" + "="*50)
    print("TRAINING METRICS")
    print("="*50)
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print("="*50)
    
    # Save artifacts using pathlib for cross-platform compatibility
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_path = output_path / "model.pkl"
    vectorizer_path = output_path / "vectorizer.pkl"
    
    print(f"\nSaving model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Saving vectorizer to {vectorizer_path}...")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("\n✓ Model training complete! Artifacts saved successfully.")
    
    return metrics


if __name__ == "__main__":
    # Default paths
    data_path = "training/sample_data.csv"
    output_dir = "backend/models/"
    
    # Allow command-line arguments
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    try:
        train_model(data_path, output_dir)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
