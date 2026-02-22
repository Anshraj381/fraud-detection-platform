"""
FastAPI application for the Intelligent Digital Fraud Awareness and Detection Platform.

This module provides the REST API interface for fraud detection, including:
- Message analysis endpoint
- Analytics dashboard endpoint
- Health check endpoint
- History management endpoint
"""

import logging
import re
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import uvicorn

from backend.analyzer import MessageAnalyzer
from backend.components.nlp_model import ModelNotFoundError, ModelCorruptedError
from backend.config import Config
from backend.utils import sanitize_input


# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Global analyzer instance
analyzer: Optional[MessageAnalyzer] = None


# Pydantic models for request/response validation
class AnalyzeRequest(BaseModel):
    """Request model for message analysis."""
    message: str = Field(..., min_length=1, max_length=Config.MAX_MESSAGE_LENGTH)
    
    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Sanitize input to prevent injection attacks."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        
        # Use the comprehensive sanitize_input function from utils
        sanitized = sanitize_input(v)
        
        return sanitized


class AnalyzeResponse(BaseModel):
    """Response model for message analysis."""
    message_text: str
    rule_score: float
    ai_probability: float
    final_risk_score: float = Field(..., alias="risk_score")
    risk_level: str
    fraud_category: str
    triggered_keywords: dict
    explanation: str
    recommendations: list
    awareness_score: float
    awareness_level: str
    timestamp: str
    
    model_config = {"populate_by_name": True}


class AnalyticsResponse(BaseModel):
    """Response model for analytics data."""
    total_messages: int
    risk_distribution: dict
    category_distribution: dict
    average_risk_score: float
    top_keywords: list
    risk_trend: list


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    model_loaded: bool
    database_connected: bool


class ClearHistoryRequest(BaseModel):
    """Request model for clearing history."""
    confirm: bool = Field(..., description="Must be true to confirm deletion")


class ClearHistoryResponse(BaseModel):
    """Response model for clearing history."""
    success: bool
    message: str


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown.
    
    Initializes MessageAnalyzer on startup and cleans up on shutdown.
    """
    global analyzer
    
    # Startup
    logger.info("Starting Fraud Detection Platform API")
    try:
        analyzer = MessageAnalyzer()
        logger.info("MessageAnalyzer initialized successfully")
    except (ModelNotFoundError, ModelCorruptedError) as e:
        logger.error(f"Failed to initialize NLP model: {e}")
        logger.warning("API starting in degraded mode (rule-based detection only)")
        # Try to initialize without the model by creating a minimal analyzer
        # For now, we'll set analyzer to None and handle it in endpoints
        analyzer = None
    except Exception as e:
        logger.critical(f"Unexpected error during startup: {e}", exc_info=True)
        # Don't raise - allow API to start even if analyzer fails
        analyzer = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Fraud Detection Platform API")
    if analyzer:
        analyzer.close()
        logger.info("MessageAnalyzer resources cleaned up")


# Initialize FastAPI application
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION,
    lifespan=lifespan
)


# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{Config.FRONTEND_PORT}",
        f"http://127.0.0.1:{Config.FRONTEND_PORT}",
        "http://localhost:8501",  # Streamlit default
        "http://127.0.0.1:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests and responses."""
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"Response: {request.method} {request.url.path} - Status {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - {e}", exc_info=True)
        raise


# Custom exception handlers
class ModelError(Exception):
    """Custom exception for model-related errors."""
    pass


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors with 400 Bad Request."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation Error", "detail": str(exc)}
    )


@app.exception_handler(ModelError)
async def model_error_handler(request: Request, exc: ModelError):
    """Handle model errors with 500 Internal Server Error."""
    logger.error(f"Model error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Model Error", "detail": "AI model is unavailable. Using rule-based detection only."}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with 500 Internal Server Error."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
    )


# API Endpoints
@app.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_message(request: AnalyzeRequest):
    """
    Analyze a message for fraud indicators.
    
    Performs complete fraud detection analysis including:
    - Rule-based pattern detection
    - AI-based classification
    - Risk scoring and categorization
    - Explanation generation
    - Awareness tracking
    
    Args:
        request: AnalyzeRequest containing the message to analyze
        
    Returns:
        AnalyzeResponse with complete analysis results
        
    Raises:
        HTTPException 400: If message validation fails
        HTTPException 500: If analysis fails
    """
    logger.info(f"Analyze request received: message_length={len(request.message)}")
    
    if not analyzer:
        logger.error("MessageAnalyzer not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis service unavailable"
        )
    
    try:
        # Perform analysis
        result = analyzer.analyze_message(request.message)
        
        # Convert datetime to ISO format string
        response_data = {
            "message_text": result.message_text,
            "rule_score": result.rule_score,
            "ai_probability": result.ai_probability,
            "risk_score": result.final_risk_score,
            "risk_level": result.risk_level,
            "fraud_category": result.fraud_category,
            "triggered_keywords": result.triggered_keywords,
            "explanation": result.explanation,
            "recommendations": result.recommendations,
            "awareness_score": result.awareness_score,
            "awareness_level": result.awareness_level,
            "timestamp": result.timestamp.isoformat()
        }
        
        logger.info(
            f"Analysis complete: risk_score={result.final_risk_score:.2f}, "
            f"category={result.fraud_category}"
        )
        
        return response_data
        
    except ValueError as e:
        logger.warning(f"Validation error during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except (ModelCorruptedError, ModelNotFoundError) as e:
        logger.error(f"Model error during analysis: {e}")
        raise ModelError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed"
        )


@app.get("/analytics", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
async def get_analytics():
    """
    Retrieve aggregated analytics data.
    
    Returns statistics including:
    - Total messages analyzed
    - Risk level distribution
    - Fraud category distribution
    - Average risk score
    - Top triggered keywords
    - Risk score trend over time
    
    Returns:
        AnalyticsResponse with aggregated statistics
        
    Raises:
        HTTPException 500: If analytics retrieval fails
    """
    logger.info("Analytics request received")
    
    if not analyzer:
        logger.error("MessageAnalyzer not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics service unavailable"
        )
    
    try:
        # Get analytics from database
        analytics = analyzer.database_logger.get_analytics()
        
        response_data = {
            "total_messages": analytics.total_messages,
            "risk_distribution": analytics.risk_distribution,
            "category_distribution": analytics.category_distribution,
            "average_risk_score": analytics.average_risk_score,
            "top_keywords": analytics.top_keywords,
            "risk_trend": analytics.risk_trend
        }
        
        logger.info(f"Analytics retrieved: total_messages={analytics.total_messages}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Check system health status.
    
    Verifies:
    - API is running
    - NLP model is loaded
    - Database connection is active
    
    Returns:
        HealthResponse with system status
    """
    logger.info("Health check request received")
    
    model_loaded = False
    database_connected = False
    
    if analyzer:
        # Check if NLP model is loaded
        try:
            model_loaded = (
                analyzer.nlp_model is not None and
                analyzer.nlp_model.model is not None and
                analyzer.nlp_model.vectorizer is not None
            )
        except Exception as e:
            logger.warning(f"Error checking model status: {e}")
        
        # Check database connection
        try:
            analyzer.database_logger.cursor.execute("SELECT 1")
            database_connected = True
        except Exception as e:
            logger.warning(f"Error checking database status: {e}")
    
    status_str = "healthy" if (model_loaded and database_connected) else "degraded"
    
    logger.info(
        f"Health check complete: status={status_str}, "
        f"model_loaded={model_loaded}, database_connected={database_connected}"
    )
    
    return {
        "status": status_str,
        "model_loaded": model_loaded,
        "database_connected": database_connected
    }


@app.delete("/history", response_model=ClearHistoryResponse, status_code=status.HTTP_200_OK)
async def clear_history(request: ClearHistoryRequest):
    """
    Clear all analysis history from database.
    
    This operation is irreversible and permanently deletes all stored analysis records.
    Requires explicit confirmation for safety.
    
    Args:
        request: ClearHistoryRequest with confirm flag (must be true)
        
    Returns:
        ClearHistoryResponse indicating success or failure
        
    Raises:
        HTTPException 400: If confirmation is not provided
        HTTPException 500: If deletion fails
    """
    logger.info(f"Clear history request received: confirm={request.confirm}")
    
    if not analyzer:
        logger.error("MessageAnalyzer not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="History service unavailable"
        )
    
    if not request.confirm:
        logger.warning("Clear history attempted without confirmation")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required. Set 'confirm' to true."
        )
    
    try:
        # Clear history from database
        success = analyzer.database_logger.clear_history(confirm=True)
        
        if success:
            logger.info("History cleared successfully")
            return {
                "success": True,
                "message": "Analysis history cleared successfully"
            }
        else:
            logger.error("Failed to clear history")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear history"
            )
            
    except ValueError as e:
        logger.warning(f"Validation error during clear history: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error clearing history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear history"
        )


# Main entry point
if __name__ == "__main__":
    logger.info(f"Starting server on {Config.API_HOST}:{Config.API_PORT}")
    uvicorn.run(
        "backend.main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=False,
        log_level=Config.LOG_LEVEL.lower()
    )
