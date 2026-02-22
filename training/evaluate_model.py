"""
Model evaluation script for the Intelligent Digital Fraud Awareness and Detection Platform.

This script loads the trained model and vectorizer, then evaluates them on test messages
to provide detailed metrics and confusion matrix.
"""

import pickle
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
import sys


def evaluate_model(model_path: str = "backend/models/model.pkl",
                   vectorizer_path: str = "backend/models/vectorizer.pkl"):
    """
    Loads trained model and vectorizer, then evaluates on test messages.
    
    Args:
        model_path: Path to trained model pickle file
        vectorizer_path: Path to trained vectorizer pickle file
    
    Raises:
        FileNotFoundError: If model or vectorizer files are not found
    """
    print("Loading trained model and vectorizer...")
    
    # Load model and vectorizer
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"✓ Model loaded from {model_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    try:
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        print(f"✓ Vectorizer loaded from {vectorizer_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Vectorizer file not found: {vectorizer_path}")
    
    # Test messages covering different fraud categories
    test_messages = [
        # OTP Scams (label: 1)
        "Share your OTP code immediately to verify your account.",
        "Urgent! Send verification code now or account will be locked.",
        
        # KYC Scams (label: 1)
        "Your KYC update is pending. Complete now to avoid account suspension.",
        "RBI mandates KYC verification. Update immediately.",
        
        # Bank Impersonation (label: 1)
        "Your SBI account is suspended. Click here to reactivate.",
        "HDFC Bank: Urgent action required on your account.",
        
        # Reward/Lottery Scams (label: 1)
        "Congratulations! You won Rs 100000 in lottery. Claim now.",
        "You are selected for cash prize. Click to receive reward.",
        
        # Phishing Links (label: 1)
        "Verify your account at http://bit.ly/verify123 immediately.",
        "Update details at http://bank-secure.xyz to unlock account.",
        
        # Legitimate messages (label: 0)
        "Your appointment is confirmed for tomorrow at 3 PM.",
        "Your order has been shipped and will arrive in 2 days.",
        "Meeting scheduled for next Monday in conference room.",
        "Your payment was successful. Receipt sent to email.",
        "Reminder: Your subscription renews next month.",
    ]
    
    # Expected labels (1 = scam, 0 = legitimate)
    expected_labels = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    
    print("\n" + "="*70)
    print("EVALUATING MODEL ON TEST MESSAGES")
    print("="*70)
    
    # Predict on test messages
    predictions = []
    probabilities = []
    
    for i, message in enumerate(test_messages):
        # Vectorize message
        message_vec = vectorizer.transform([message])
        
        # Predict
        prediction = model.predict(message_vec)[0]
        probability = model.predict_proba(message_vec)[0][1] * 100  # Fraud probability
        
        predictions.append(prediction)
        probabilities.append(probability)
        
        # Display result
        label = "SCAM" if prediction == 1 else "LEGITIMATE"
        expected = "SCAM" if expected_labels[i] == 1 else "LEGITIMATE"
        match = "✓" if prediction == expected_labels[i] else "✗"
        
        print(f"\n{match} Message {i+1}:")
        print(f"   Text: {message[:60]}...")
        print(f"   Predicted: {label} (probability: {probability:.2f}%)")
        print(f"   Expected: {expected}")
    
    # Calculate metrics
    print("\n" + "="*70)
    print("DETAILED METRICS")
    print("="*70)
    
    print("\nClassification Report:")
    print(classification_report(expected_labels, predictions, 
                                target_names=['Legitimate', 'Scam'],
                                digits=4))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(expected_labels, predictions)
    print(f"                 Predicted")
    print(f"                 Legitimate  Scam")
    print(f"Actual Legitimate    {cm[0][0]:3d}      {cm[0][1]:3d}")
    print(f"       Scam          {cm[1][0]:3d}      {cm[1][1]:3d}")
    
    # Calculate accuracy
    correct = sum(1 for p, e in zip(predictions, expected_labels) if p == e)
    accuracy = correct / len(expected_labels) * 100
    
    print(f"\nOverall Accuracy: {accuracy:.2f}% ({correct}/{len(expected_labels)} correct)")
    
    print("\n" + "="*70)
    print("✓ Evaluation complete!")
    print("="*70)


if __name__ == "__main__":
    # Allow command-line arguments
    model_path = "backend/models/model.pkl"
    vectorizer_path = "backend/models/vectorizer.pkl"
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    if len(sys.argv) > 2:
        vectorizer_path = sys.argv[2]
    
    try:
        evaluate_model(model_path, vectorizer_path)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
