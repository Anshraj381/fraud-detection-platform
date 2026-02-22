"""
Utility functions for the Intelligent Digital Fraud Awareness and Detection Platform.

This module provides helper functions for input sanitization, logging setup,
and input validation to ensure security and proper error handling.
"""

import html
import re
import logging
from typing import Optional

from backend.config import Config


def sanitize_input(message: str) -> str:
    """
    Sanitizes user input to prevent injection attacks.
    
    This function performs multiple sanitization steps:
    1. Removes HTML script tags to prevent XSS attacks
    2. Escapes single quotes for SQL injection prevention (defense in depth)
    3. Escapes HTML entities
    4. Limits message length to configured maximum
    
    Args:
        message: Raw user input message
        
    Returns:
        Sanitized message safe for processing and storage
        
    Examples:
        >>> sanitize_input("<script>alert('xss')</script>Hello")
        "Hello"
        >>> sanitize_input("Test's message")
        "Test''s message"
    """
    logger = logging.getLogger(__name__)
    original_length = len(message)
    
    # Remove potential script tags (XSS prevention)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove other potentially dangerous HTML tags
    sanitized = re.sub(r'<iframe[^>]*>.*?</iframe>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<object[^>]*>.*?</object>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<embed[^>]*>', '', sanitized, flags=re.IGNORECASE)
    
    # SQL injection prevention - escape single quotes (defense in depth, parameterized queries are primary defense)
    # Note: This is done before HTML escaping to preserve the SQL escaping
    sanitized = sanitized.replace("'", "''")
    
    # HTML escape (converts < > & " to entities)
    # Note: We don't escape single quotes here since we already handled them for SQL
    sanitized = html.escape(sanitized, quote=False)
    
    # Limit length
    if len(sanitized) > Config.MAX_MESSAGE_LENGTH:
        sanitized = sanitized[:Config.MAX_MESSAGE_LENGTH]
        logger.warning(
            f"Message truncated during sanitization: "
            f"original_length={original_length}, "
            f"sanitized_length={len(sanitized)}, "
            f"max_length={Config.MAX_MESSAGE_LENGTH}"
        )
    
    if original_length != len(sanitized):
        logger.info(
            f"Input sanitized: original_length={original_length}, "
            f"sanitized_length={len(sanitized)}"
        )
    
    return sanitized


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configures logging with file and console handlers.
    
    Sets up comprehensive logging for the application with:
    - File handler for persistent logs
    - Console handler for real-time monitoring
    - Configurable log level, file path, and format
    - Proper formatting with timestamps and context
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   Defaults to Config.LOG_LEVEL.
        log_file: Path to log file. Defaults to Config.LOG_FILE.
        log_format: Log message format string. Defaults to Config.LOG_FORMAT.
        
    Examples:
        >>> setup_logging()  # Use defaults from Config
        >>> setup_logging(log_level="DEBUG", log_file="debug.log")
    """
    # Use config defaults if not specified
    level = log_level or Config.LOG_LEVEL
    file_path = log_file or str(Config.LOG_FILE)
    format_str = log_format or Config.LOG_FORMAT
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_str,
        handlers=[
            logging.FileHandler(file_path, mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True  # Override any existing configuration
    )
    
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={level}, file={file_path}, format={format_str}"
    )


def validate_message_input(message: str) -> None:
    """
    Validates message input before processing.
    
    Performs validation checks:
    1. Message is not empty or whitespace-only
    2. Message does not exceed maximum length
    
    Args:
        message: Input message to validate
        
    Raises:
        ValueError: If message is empty or exceeds length limit
        
    Examples:
        >>> validate_message_input("Valid message")  # No exception
        >>> validate_message_input("")  # Raises ValueError
        >>> validate_message_input("x" * 6000)  # Raises ValueError
    """
    logger = logging.getLogger(__name__)
    
    # Check for empty message
    if not message or not message.strip():
        logger.warning("Empty message submitted for validation")
        raise ValueError("Message cannot be empty")
    
    # Check length limit
    if len(message) > Config.MAX_MESSAGE_LENGTH:
        logger.warning(
            f"Message exceeds length limit: "
            f"length={len(message)}, max={Config.MAX_MESSAGE_LENGTH}"
        )
        raise ValueError(
            f"Message exceeds {Config.MAX_MESSAGE_LENGTH} character limit "
            f"(received {len(message)} characters)"
        )
    
    logger.debug(f"Message validated: length={len(message)}")


def validate_score_range(score: float, score_name: str = "score") -> None:
    """
    Validates that a score is within the valid range [0, 100].
    
    Args:
        score: Score value to validate
        score_name: Name of the score for error messages
        
    Raises:
        ValueError: If score is outside [0, 100] range
        
    Examples:
        >>> validate_score_range(50.0, "risk_score")  # No exception
        >>> validate_score_range(-10.0, "ai_score")  # Raises ValueError
        >>> validate_score_range(150.0, "rule_score")  # Raises ValueError
    """
    if not (0 <= score <= 100):
        raise ValueError(
            f"{score_name} must be between 0 and 100 (received {score})"
        )


def validate_risk_level(risk_level: str) -> None:
    """
    Validates that a risk level is one of the valid values.
    
    Args:
        risk_level: Risk level string to validate
        
    Raises:
        ValueError: If risk level is not valid
        
    Examples:
        >>> validate_risk_level("Safe")  # No exception
        >>> validate_risk_level("Invalid")  # Raises ValueError
    """
    valid_levels = {
        Config.RISK_LEVEL_SAFE,
        Config.RISK_LEVEL_SUSPICIOUS,
        Config.RISK_LEVEL_HIGH_RISK
    }
    
    if risk_level not in valid_levels:
        raise ValueError(
            f"Invalid risk level: {risk_level}. "
            f"Must be one of {valid_levels}"
        )
