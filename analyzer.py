"""
Message Analyzer orchestrator for the Intelligent Digital Fraud Awareness and Detection Platform.

This module coordinates all fraud detection components to perform complete message analysis,
including rule-based detection, AI classification, risk scoring, category classification,
explanation generation, awareness tracking, and database logging.
"""

import logging
from datetime import datetime
from typing import Optional

from backend.components.rule_engine import RuleEngine
from backend.components.nlp_model import NLPModel, ModelNotFoundError, ModelCorruptedError
from backend.components.risk_scorer import RiskScorer
from backend.components.category_classifier import CategoryClassifier
from backend.components.explainability import ExplainabilityModule
from backend.components.database_logger import DatabaseLogger
from backend.components.awareness_tracker import AwarenessTracker
from backend.models.data_models import AnalysisResult
from backend.config import Config


# Configure logging
logger = logging.getLogger(__name__)


class MessageAnalyzer:
    """
    Orchestrates the complete fraud detection analysis pipeline.
    
    The MessageAnalyzer coordinates all detection components to provide comprehensive
    fraud analysis, including:
    - Rule-based pattern detection
    - AI-based classification
    - Risk score calculation and level classification
    - Fraud category identification
    - Human-readable explanations and recommendations
    - User awareness tracking
    - Database persistence
    
    Features:
    - Input validation (length, non-empty)
    - Graceful degradation when components fail
    - Comprehensive error handling
    - Performance logging
    - Complete analysis pipeline in < 2 seconds
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        vectorizer_path: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        """
        Initialize MessageAnalyzer with all required components.
        
        Args:
            model_path: Path to NLP model pickle file (defaults to Config.MODEL_PATH)
            vectorizer_path: Path to vectorizer pickle file (defaults to Config.VECTORIZER_PATH)
            db_path: Path to SQLite database (defaults to Config.DB_PATH)
            
        Raises:
            ModelNotFoundError: If NLP model files are missing
            ModelCorruptedError: If NLP model files are corrupted
        """
        logger.info("Initializing MessageAnalyzer")
        
        # Initialize all components
        try:
            self.rule_engine = RuleEngine()
            logger.info("RuleEngine initialized")
            
            self.nlp_model = NLPModel(model_path, vectorizer_path)
            logger.info("NLPModel initialized")
            
            self.risk_scorer = RiskScorer()
            logger.info("RiskScorer initialized")
            
            self.category_classifier = CategoryClassifier()
            logger.info("CategoryClassifier initialized")
            
            self.explainability_module = ExplainabilityModule()
            logger.info("ExplainabilityModule initialized")
            
            self.database_logger = DatabaseLogger(db_path)
            logger.info("DatabaseLogger initialized")
            
            self.awareness_tracker = AwarenessTracker()
            logger.info("AwarenessTracker initialized")
            
            logger.info("MessageAnalyzer initialization complete")
            
        except (ModelNotFoundError, ModelCorruptedError) as e:
            logger.critical(f"Failed to initialize MessageAnalyzer: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error during MessageAnalyzer initialization: {e}", exc_info=True)
            raise
    
    def analyze_message(self, message: str) -> AnalysisResult:
        """
        Performs complete fraud analysis pipeline on a message.
        
        Pipeline steps:
        1. Validate input (non-empty, max 5000 characters)
        2. Run Rule Engine analysis
        3. Run NLP Model prediction (with graceful degradation on failure)
        4. Calculate risk score and level
        5. Classify fraud category
        6. Generate explanation and recommendations
        7. Query awareness tracker for current score
        8. Log to database
        9. Return complete AnalysisResult
        
        Args:
            message: Input text to analyze (max 5000 characters)
            
        Returns:
            AnalysisResult containing all detection results:
                - message_text: Original message
                - rule_score: Rule-based score (0-100)
                - ai_probability: AI fraud probability (0-100)
                - final_risk_score: Combined risk score (0-100)
                - risk_level: Risk classification (Safe/Suspicious/High Risk)
                - fraud_category: Detected fraud type
                - triggered_keywords: Dictionary of triggered keywords by category
                - explanation: Human-readable explanation
                - recommendations: List of safety recommendations
                - awareness_score: Current user awareness score (0-100)
                - awareness_level: User awareness level classification
                - timestamp: Analysis timestamp
                
        Raises:
            ValueError: If message is empty or exceeds length limit
        """
        start_time = datetime.now()
        logger.info(f"Starting message analysis: length={len(message)}")
        
        # Step 1: Validate input
        self._validate_input(message)
        
        try:
            # Step 2: Run Rule Engine analysis
            logger.info("Running Rule Engine analysis")
            rule_result = self.rule_engine.analyze(message)
            rule_score = rule_result.rule_score
            triggered_keywords = rule_result.triggered_keywords
            pattern_weights = rule_result.pattern_weights
            logger.info(f"Rule Engine complete: score={rule_score:.2f}, patterns={len(triggered_keywords)}")
            
            # Step 3: Run NLP Model prediction (with graceful degradation)
            ai_probability = self._run_nlp_analysis(message)
            
            # Step 4: Calculate risk score and level
            logger.info("Calculating risk score")
            risk_assessment = self.risk_scorer.calculate_risk(rule_score, ai_probability)
            final_risk_score = risk_assessment.final_score
            risk_level = risk_assessment.risk_level
            logger.info(f"Risk assessment complete: score={final_risk_score:.2f}, level={risk_level}")
            
            # Step 5: Classify fraud category
            logger.info("Classifying fraud category")
            fraud_category = self.category_classifier.classify(triggered_keywords, pattern_weights)
            logger.info(f"Category classification complete: category={fraud_category}")
            
            # Step 6: Query awareness tracker for current score
            logger.info("Calculating awareness score")
            awareness_score_obj = self._calculate_awareness()
            awareness_score = awareness_score_obj.score
            awareness_level = awareness_score_obj.level
            logger.info(f"Awareness tracking complete: score={awareness_score:.2f}, level={awareness_level}")
            
            # Create preliminary AnalysisResult for explanation generation
            timestamp = datetime.now()
            analysis_result = AnalysisResult(
                message_text=message,
                rule_score=rule_score,
                ai_probability=ai_probability,
                final_risk_score=final_risk_score,
                risk_level=risk_level,
                fraud_category=fraud_category,
                triggered_keywords=triggered_keywords,
                explanation="",  # Will be filled by explainability module
                recommendations=[],  # Will be filled by explainability module
                awareness_score=awareness_score,
                awareness_level=awareness_level,
                timestamp=timestamp
            )
            
            # Step 7: Generate explanation and recommendations
            logger.info("Generating explanation and recommendations")
            explanation_obj = self.explainability_module.generate_explanation(analysis_result)
            
            # Update analysis result with explanation
            analysis_result.explanation = explanation_obj.explanation_text
            analysis_result.recommendations = explanation_obj.recommendations
            logger.info("Explanation generation complete")
            
            # Step 8: Log to database
            logger.info("Logging analysis to database")
            log_success = self.database_logger.log_analysis(analysis_result)
            if not log_success:
                logger.warning("Database logging failed, but continuing with analysis")
            
            # Calculate total execution time
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Message analysis complete: "
                f"risk_score={final_risk_score:.2f}, "
                f"category={fraud_category}, "
                f"elapsed_time={elapsed_time:.3f}s"
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during message analysis: {e}", exc_info=True)
            raise
    
    def _validate_input(self, message: str) -> None:
        """
        Validates message input.
        
        Args:
            message: Input text to validate
            
        Raises:
            ValueError: If message is empty or exceeds length limit
        """
        # Check if message is empty or only whitespace
        if not message or not message.strip():
            logger.warning("Empty message submitted")
            raise ValueError("Message cannot be empty")
        
        # Check if message exceeds maximum length
        if len(message) > Config.MAX_MESSAGE_LENGTH:
            logger.warning(f"Message exceeds length limit: {len(message)} characters")
            raise ValueError(
                f"Message exceeds maximum length of {Config.MAX_MESSAGE_LENGTH} characters"
            )
        
        logger.info(f"Input validation passed: length={len(message)}")
    
    def _run_nlp_analysis(self, message: str) -> float:
        """
        Runs NLP model prediction with graceful degradation on failure.
        
        If the NLP model fails, logs the error and returns 0.0 to allow
        the system to continue with rule-based detection only.
        
        Args:
            message: Input text to analyze
            
        Returns:
            AI fraud probability (0-100), or 0.0 if model fails
        """
        try:
            logger.info("Running NLP Model prediction")
            ai_probability = self.nlp_model.predict_probability(message)
            logger.info(f"NLP Model complete: probability={ai_probability:.2f}")
            return ai_probability
            
        except (ModelCorruptedError, Exception) as e:
            # Graceful degradation: continue with rule-based detection only
            logger.error(
                f"NLP Model prediction failed, using rule-based detection only: {e}",
                exc_info=True
            )
            logger.warning("System degraded: AI analysis unavailable, using rule-based detection only")
            return 0.0
    
    def _calculate_awareness(self) -> 'AwarenessScore':
        """
        Calculates current user awareness score based on analysis history.
        
        Queries the database for all past analyses and calculates awareness
        score using the AwarenessTracker. If database query fails, returns
        a default beginner score.
        
        Returns:
            AwarenessScore object with score, level, and metrics
        """
        try:
            # Query database for all past analyses
            self.database_logger.cursor.execute("""
                SELECT risk_level
                FROM analyses
                ORDER BY timestamp ASC
            """)
            
            # Create simple objects with risk_level attribute for awareness tracker
            class AnalysisRecord:
                def __init__(self, risk_level: str):
                    self.risk_level = risk_level
            
            user_history = [
                AnalysisRecord(row['risk_level'])
                for row in self.database_logger.cursor.fetchall()
            ]
            
            # Calculate awareness score
            awareness_score = self.awareness_tracker.calculate_awareness(user_history)
            
            return awareness_score
            
        except Exception as e:
            # Fallback to default beginner score if database query fails
            logger.warning(f"Failed to calculate awareness score, using default: {e}")
            from backend.models.data_models import AwarenessScore
            return AwarenessScore(
                score=0.0,
                level="Beginner",
                high_risk_percentage=0.0,
                usage_frequency_factor=0.0
            )
    
    def close(self) -> None:
        """
        Closes database connection and cleans up resources.
        
        Should be called when the MessageAnalyzer is no longer needed.
        """
        try:
            self.database_logger.close()
            logger.info("MessageAnalyzer resources cleaned up")
        except Exception as e:
            logger.error(f"Error during MessageAnalyzer cleanup: {e}", exc_info=True)
    
    def __del__(self):
        """Ensures resources are cleaned up on object destruction."""
        self.close()
