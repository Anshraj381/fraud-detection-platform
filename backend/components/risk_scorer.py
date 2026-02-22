"""
Risk Scorer component for the Intelligent Digital Fraud Awareness and Detection Platform.

This module combines rule-based and AI scores to produce final risk assessments.
"""

import logging
from backend.models.data_models import RiskAssessment


# Configure logging
logger = logging.getLogger(__name__)


class RiskScorer:
    """
    Combines rule-based and AI scores to calculate final risk assessment.
    
    The Risk Scorer applies a weighted formula to combine detection scores from
    the Rule Engine (40% weight) and NLP Model (60% weight), then classifies
    the result into risk levels.
    """
    
    # Risk level thresholds
    SAFE_THRESHOLD = 30
    SUSPICIOUS_THRESHOLD = 70
    
    def calculate_risk(self, rule_score: float, ai_score: float) -> RiskAssessment:
        """
        Calculates final risk score and level.
        
        Applies the formula: final_score = (rule_score × 0.4) + (ai_score × 0.6)
        
        Args:
            rule_score: Score from Rule Engine (0-100)
            ai_score: Probability from NLP Model (0-100)
            
        Returns:
            RiskAssessment containing:
                - final_score: float (0-100) - Combined risk score
                - risk_level: str - Classification label:
                    * "Safe" for scores 0-30
                    * "Suspicious" for scores 31-70
                    * "High Risk" for scores 71-100
        
        Examples:
            >>> scorer = RiskScorer()
            >>> result = scorer.calculate_risk(20, 30)
            >>> result.final_score
            26.0
            >>> result.risk_level
            'Safe'
        """
        logger.info(f"Calculating risk: rule_score={rule_score:.2f}, ai_score={ai_score:.2f}")
        
        # Apply weighted formula: 40% rule-based, 60% AI-based
        final_score = (rule_score * 0.7) + (ai_score * 0.3)
        
        # Classify risk level based on thresholds
        if final_score <= self.SAFE_THRESHOLD:
            risk_level = "Safe"
        elif final_score <= self.SUSPICIOUS_THRESHOLD:
            risk_level = "Suspicious"
        else:
            risk_level = "High Risk"
        
        logger.info(
            f"Risk calculation complete: final_score={final_score:.2f}, "
            f"risk_level={risk_level}"
        )
        
        return RiskAssessment(
            final_score=final_score,
            risk_level=risk_level
        )
