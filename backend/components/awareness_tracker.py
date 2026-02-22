"""
Awareness Tracker component for the Intelligent Digital Fraud Awareness and Detection Platform.

This module calculates and tracks user awareness scores based on usage patterns.
"""

import logging
from typing import List
from backend.models.data_models import AwarenessScore


# Configure logging
logger = logging.getLogger(__name__)


class AwarenessTracker:
    """
    Calculates user awareness scores based on usage patterns.
    
    The Awareness Tracker rewards users who consistently analyze high-risk messages
    (60% weight) while also considering usage frequency with diminishing returns
    after 50 analyses (40% weight).
    """
    
    # Awareness level thresholds
    BEGINNER_THRESHOLD = 40
    IMPROVING_THRESHOLD = 60
    AWARE_THRESHOLD = 80
    
    # Usage frequency diminishing returns threshold
    FREQUENCY_THRESHOLD = 50
    
    def calculate_awareness(self, user_history: List) -> AwarenessScore:
        """
        Calculates user awareness score based on analysis history.
        
        Applies the formula:
        awareness_score = (high_risk_percentage × 0.6) + (usage_frequency_factor × 0.4)
        
        where:
            high_risk_percentage = (count of high-risk messages / total messages) × 100
            usage_frequency_factor = min(100, (total_analyses / 50) × 100)
        
        Args:
            user_history: List of analysis records containing risk_level information
            
        Returns:
            AwarenessScore containing:
                - score: float (0-100) - Calculated awareness score
                - level: str - Classification label:
                    * "Beginner" for scores 0-40
                    * "Improving" for scores 41-60
                    * "Aware" for scores 61-80
                    * "Highly Aware" for scores 81-100
                - high_risk_percentage: float - Percentage of high-risk messages analyzed
                - usage_frequency_factor: float - Factor based on total usage count
        
        Examples:
            >>> tracker = AwarenessTracker()
            >>> history = [
            ...     AnalysisRecord(risk_level="High Risk"),
            ...     AnalysisRecord(risk_level="High Risk"),
            ...     AnalysisRecord(risk_level="Safe")
            ... ]
            >>> result = tracker.calculate_awareness(history)
            >>> result.high_risk_percentage
            66.67
            >>> result.level
            'Improving'
        """
        logger.info(f"Calculating awareness: history_size={len(user_history)}")
        
        # Handle empty history
        if not user_history:
            logger.info("Empty history, returning Beginner level with score 0")
            return AwarenessScore(
                score=0.0,
                level="Beginner",
                high_risk_percentage=0.0,
                usage_frequency_factor=0.0
            )
        
        # Calculate total analyses
        total_analyses = len(user_history)
        
        # Count high-risk messages
        high_risk_count = sum(
            1 for record in user_history 
            if hasattr(record, 'risk_level') and record.risk_level == "High Risk"
        )
        
        # Calculate high_risk_percentage
        high_risk_percentage = (high_risk_count / total_analyses) * 100
        
        # Calculate usage_frequency_factor with diminishing returns after 50 analyses
        usage_frequency_factor = min(100.0, (total_analyses / self.FREQUENCY_THRESHOLD) * 100)
        
        # Apply weighted formula: 60% high-risk focus, 40% usage frequency
        awareness_score = (high_risk_percentage * 0.6) + (usage_frequency_factor * 0.4)
        
        # Classify awareness level based on thresholds
        if awareness_score <= self.BEGINNER_THRESHOLD:
            awareness_level = "Beginner"
        elif awareness_score <= self.IMPROVING_THRESHOLD:
            awareness_level = "Improving"
        elif awareness_score <= self.AWARE_THRESHOLD:
            awareness_level = "Aware"
        else:
            awareness_level = "Highly Aware"
        
        logger.info(
            f"Awareness calculated: score={awareness_score:.2f}, level={awareness_level}, "
            f"high_risk_count={high_risk_count}/{total_analyses}, "
            f"high_risk_percentage={high_risk_percentage:.2f}%, "
            f"usage_frequency_factor={usage_frequency_factor:.2f}"
        )
        
        return AwarenessScore(
            score=awareness_score,
            level=awareness_level,
            high_risk_percentage=high_risk_percentage,
            usage_frequency_factor=usage_frequency_factor
        )
