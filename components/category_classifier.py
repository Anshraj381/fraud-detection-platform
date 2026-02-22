"""
Category classification for fraud detection.

This module determines the specific type of fraud based on triggered patterns
and their weighted scores.
"""

import logging
from typing import Dict, List


# Configure logging
logger = logging.getLogger(__name__)


class CategoryClassifier:
    """
    Classifies fraud messages into specific categories based on triggered patterns.
    
    The classifier analyzes triggered keywords and their weights to determine
    the primary fraud category. If no clear category dominates, it returns
    "Other/Unknown".
    """
    
    def __init__(self):
        """
        Initialize the CategoryClassifier with category mappings.
        
        Maps pattern categories from RuleEngine to fraud categories:
        - otp -> OTP Scam
        - bank_kyc -> KYC Scam or Bank Impersonation
        - rewards -> Reward/Lottery Scam
        - urls -> Phishing Link Scam
        """
        # Mapping from pattern categories to fraud categories
        self.category_mapping = {
            "otp": "OTP Scam",
            "bank_kyc": "Bank Impersonation",  # Default for bank_kyc
            "rewards": "Reward/Lottery Scam",
            "urls": "Phishing Link Scam"
        }
        
        # KYC-specific keywords that indicate KYC Scam vs Bank Impersonation
        self.kyc_keywords = ["kyc", "kyc update", "update kyc", "pan card", "aadhar"]
    
    def classify(self, triggered_keywords: Dict[str, List[str]], 
                 pattern_weights: Dict[str, float]) -> str:
        """
        Identifies the primary fraud category based on triggered patterns.
        
        Args:
            triggered_keywords: Dictionary mapping category names to lists of triggered keywords
            pattern_weights: Dictionary mapping category names to their weight contributions
            
        Returns:
            Primary fraud category:
                - "OTP Scam"
                - "KYC Scam"
                - "Bank Impersonation"
                - "Reward/Lottery Scam"
                - "Phishing Link Scam"
                - "Other/Unknown"
        """
        logger.info(f"Classifying fraud category: patterns_count={len(pattern_weights)}")
        
        # If no patterns triggered, return Other/Unknown
        if not pattern_weights:
            logger.info("No patterns triggered, returning Other/Unknown")
            return "Other/Unknown"
        
        # Calculate total score
        total_score = sum(pattern_weights.values())
        
        # If total score is too low (less than 10% threshold), return Other/Unknown
        if total_score < 10:
            logger.info(f"Total score too low ({total_score:.2f}), returning Other/Unknown")
            return "Other/Unknown"
        
        # Find the category with the highest weight
        max_category = max(pattern_weights.items(), key=lambda x: x[1])
        max_category_name = max_category[0]
        max_weight = max_category[1]
        
        logger.info(
            f"Dominant category: {max_category_name}, "
            f"weight={max_weight:.2f}, total_score={total_score:.2f}"
        )
        
        # Check if the highest weight is dominant (at least 10% of total score)
        # This ensures a clear category dominates
        if max_weight < (total_score * 0.1):
            logger.warning(
                f"No clear dominant category (max_weight={max_weight:.2f} < "
                f"10% of total={total_score * 0.1:.2f}), returning Other/Unknown"
            )
            return "Other/Unknown"
        
        # Special handling for bank_kyc category
        if max_category_name == "bank_kyc":
            # Check if KYC-specific keywords are present
            if "bank_kyc" in triggered_keywords:
                keywords_lower = [kw.lower() for kw in triggered_keywords["bank_kyc"]]
                has_kyc_keyword = any(
                    kyc_kw in keywords_lower 
                    for kyc_kw in self.kyc_keywords
                )
                
                if has_kyc_keyword:
                    logger.info("KYC-specific keywords detected, classifying as KYC Scam")
                    return "KYC Scam"
                else:
                    logger.info("Bank keywords without KYC, classifying as Bank Impersonation")
                    return "Bank Impersonation"
        
        # Map the category to fraud category
        fraud_category = self.category_mapping.get(max_category_name, "Other/Unknown")
        
        logger.info(f"Classification complete: fraud_category={fraud_category}")
        
        return fraud_category
