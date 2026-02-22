"""
NLP-based fraud detection model.

This module implements the machine learning classifier for sophisticated fraud detection
using TF-IDF vectorization and Logistic Regression.
"""

import pickle
import logging
from pathlib import Path
from typing import Optional

from backend.config import Config


# Configure logging
logger = logging.getLogger(__name__)


class ModelNotFoundError(Exception):
    """Raised when model files are missing."""
    pass


class ModelCorruptedError(Exception):
    """Raised when model files are corrupted or cannot be loaded."""
    pass


class NLPModel:
    """
    Offline ML classifier for fraud detection.
    
    Uses pre-trained TF-IDF vectorizer and Logistic Regression model to predict
    fraud probability for input messages.
    
    Attributes:
        model: Loaded Logistic Regression classifier
        vectorizer: Loaded TF-IDF vectorizer
        model_path: Path to the model pickle file
        vectorizer_path: Path to the vectorizer pickle file
    """
    
    def __init__(self, model_path: Optional[str] = None, vectorizer_path: Optional[str] = None):
        """
        Initialize NLPModel by loading pre-trained model and vectorizer.
        
        Args:
            model_path: Path to the trained model pickle file (defaults to Config.MODEL_PATH)
            vectorizer_path: Path to the vectorizer pickle file (defaults to Config.VECTORIZER_PATH)
            
        Raises:
            ModelNotFoundError: If model files are missing
            ModelCorruptedError: If model files are corrupted or cannot be loaded
        """
        self.model_path = Path(model_path) if model_path else Config.MODEL_PATH
        self.vectorizer_path = Path(vectorizer_path) if vectorizer_path else Config.VECTORIZER_PATH
        
        self.model = None
        self.vectorizer = None
        
        self._load_models()
        
        logger.info(
            f"NLPModel initialized successfully: model={self.model_path}, "
            f"vectorizer={self.vectorizer_path}"
        )
    
    def _load_models(self) -> None:
        """
        Load model and vectorizer from pickle files.
        
        Raises:
            ModelNotFoundError: If model files don't exist
            ModelCorruptedError: If model files cannot be loaded
        """
        # Check if files exist
        if not self.model_path.exists():
            error_msg = f"Model file not found: {self.model_path}"
            logger.critical(error_msg)
            raise ModelNotFoundError(error_msg)
        
        if not self.vectorizer_path.exists():
            error_msg = f"Vectorizer file not found: {self.vectorizer_path}"
            logger.critical(error_msg)
            raise ModelNotFoundError(error_msg)
        
        # Load model
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            error_msg = f"Failed to load model from {self.model_path}: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            raise ModelCorruptedError(error_msg)
        
        # Load vectorizer
        try:
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            logger.info(f"Vectorizer loaded successfully from {self.vectorizer_path}")
        except Exception as e:
            error_msg = f"Failed to load vectorizer from {self.vectorizer_path}: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            raise ModelCorruptedError(error_msg)
    
    def predict_probability(self, message: str) -> float:
        """
        Predict fraud probability for a given message.
        
        Uses TF-IDF vectorization followed by Logistic Regression prediction
        to calculate the probability that the message is fraudulent.
        
        Args:
            message: Input text message to classify
            
        Returns:
            Fraud probability score between 0 and 100 (percentage)
            
        Raises:
            ValueError: If message is empty or invalid
            ModelCorruptedError: If prediction fails due to model issues
        """
        # Validate input
        if not message or not message.strip():
            logger.warning("Empty message provided for prediction")
            return 0.0
        
        try:
            # Vectorize the message
            message_vectorized = self.vectorizer.transform([message])
            
            # Predict probability (returns array of [prob_class_0, prob_class_1])
            probabilities = self.model.predict_proba(message_vectorized)
            
            # Extract fraud probability (class 1) and convert to percentage
            fraud_probability = probabilities[0][1] * 100
            
            logger.info(
                f"NLP prediction complete: probability={fraud_probability:.2f}, "
                f"message_length={len(message)}"
            )
            
            return float(fraud_probability)
            
        except Exception as e:
            error_msg = f"Prediction failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ModelCorruptedError(error_msg)
