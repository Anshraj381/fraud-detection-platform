"""
Configuration constants for the Intelligent Digital Fraud Awareness and Detection Platform.

This module centralizes all configuration settings including file paths, thresholds,
and system parameters.
"""

from pathlib import Path


class Config:
    """Central configuration class for the fraud detection platform."""
    
    # Base directory
    BASE_DIR = Path(__file__).parent.parent
    
    # Model paths
    MODEL_PATH = BASE_DIR / "backend" / "models" / "model.pkl"
    VECTORIZER_PATH = BASE_DIR / "backend" / "models" / "vectorizer.pkl"
    
    # Database configuration
    DB_PATH = BASE_DIR / "fraud_detection.db"
    DB_TIMEOUT = 5.0
    DB_MAX_RETRIES = 3
    
    # Risk level thresholds
    SAFE_THRESHOLD = 30
    SUSPICIOUS_THRESHOLD = 70
    
    # Risk level labels
    RISK_LEVEL_SAFE = "Safe"
    RISK_LEVEL_SUSPICIOUS = "Suspicious"
    RISK_LEVEL_HIGH_RISK = "High Risk"
    
    # Message constraints
    MAX_MESSAGE_LENGTH = 5000
    
    # Analysis weights
    RULE_WEIGHT = 0.4
    AI_WEIGHT = 0.6
    
    # Awareness tracking weights
    AWARENESS_HIGH_RISK_WEIGHT = 0.6
    AWARENESS_USAGE_WEIGHT = 0.4
    AWARENESS_USAGE_THRESHOLD = 50  # Diminishing returns after this many analyses
    
    # Awareness level thresholds
    AWARENESS_BEGINNER_THRESHOLD = 40
    AWARENESS_IMPROVING_THRESHOLD = 60
    AWARENESS_AWARE_THRESHOLD = 80
    
    # Awareness level labels
    AWARENESS_LEVEL_BEGINNER = "Beginner"
    AWARENESS_LEVEL_IMPROVING = "Improving"
    AWARENESS_LEVEL_AWARE = "Aware"
    AWARENESS_LEVEL_HIGHLY_AWARE = "Highly Aware"
    
    # Performance constraints
    ANALYSIS_TIMEOUT = 2.0  # seconds
    NLP_INFERENCE_TIMEOUT = 0.5  # seconds
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = BASE_DIR / "fraud_detection.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # API configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_TITLE = "Intelligent Digital Fraud Awareness and Detection Platform"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Offline fraud detection system combining rule-based and ML approaches"
    
    # Frontend configuration
    FRONTEND_PORT = 8501
    
    # Model training configuration
    TFIDF_MAX_FEATURES = 5000
    TFIDF_NGRAM_RANGE = (1, 2)
    LOGISTIC_REGRESSION_MAX_ITER = 1000
    TRAIN_TEST_SPLIT_RATIO = 0.2
    MIN_TRAINING_SAMPLES = 100
