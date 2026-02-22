"""
Rule-based fraud detection engine.

This module implements pattern matching and keyword detection for identifying
suspicious messages based on predefined rules and weights.
"""

import re
import logging
from typing import Dict, List, Set
from backend.models.data_models import RuleResult


# Configure logging
logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Rule-based fraud detection engine that analyzes messages for suspicious patterns.
    
    The engine uses weighted pattern categories to calculate a risk score based on
    keyword detection and brand-domain mismatch analysis.
    """
    
    def __init__(self):
        """
        Initialize the RuleEngine with pattern categories and their weights.
        
        Pattern weights:
        - Urgency keywords: 25
        - OTP requests: 35
        - Financial keywords: 25
        - Bank/KYC keywords: 20
        - Reward scams: 15
        - URLs: 10
        - Brand-domain mismatch: 20
        """
        # Define pattern categories with their weights
        self.pattern_weights = {
            "urgency": 25,
            "otp": 35,
            "financial": 25,
            "bank_kyc": 20,
            "rewards": 15,
            "urls": 10,
            "brand_mismatch": 20
        }
        
        # Define keyword patterns for each category
        self.patterns = {
            "urgency": [
                "urgent", "immediately", "act now", "final notice", "limited time",
                "expire", "expires", "last chance", "hurry", "quick", "asap",
                "important", "critical", "warning", "alert", "action required",
                "unauthorized", "suspicious", "fraud", "cancel", "stop", "prevent",
                "attention", "must", "required", "deadline", "time sensitive",
                "confirm now", "respond now", "verify now", "update now"
            ],
            "otp": [
                "otp", "verification code", "one time password", "share code",
                "verify", "authentication code", "security code", "pin code",
                "share otp", "send otp", "provide otp", "enter otp", "submit otp",
                "otp code", "6 digit", "4 digit", "verification pin", "auth code",
                "confirm code", "access code", "passcode", "secret code"
            ],
            "financial": [
                "payment", "transaction", "money", "account", "card", "debit",
                "credit", "transfer", "withdraw", "deposit", "balance", "fund",
                "refund", "charge", "fee", "amount", "rupees", "rs", "inr",
                "dollar", "usd", "bank account", "credit card", "debit card",
                "wallet", "paytm", "phonepe", "gpay", "upi", "net banking",
                "online banking", "mobile banking", "payment failed",
                "payment pending", "transaction failed", "unauthorized transaction",
                "suspicious activity"
            ],
            "bank_kyc": [
                "rbi", "sbi", "hdfc", "kyc update", "account suspended",
                "kyc", "bank", "icici", "axis", "account blocked", "verify account",
                "update kyc", "pan card", "aadhar", "account locked", "account frozen",
                "account closed", "account deactivated", "kyc verification",
                "kyc pending", "kyc expired", "update details", "verify identity",
                "identity verification", "document verification", "kotak", "yes bank",
                "idbi", "pnb", "canara", "union bank", "bank of india",
                "central bank", "reserve bank"
            ],
            "rewards": [
                "congratulations", "lottery", "prize", "won", "cash reward",
                "winner", "claim", "free gift", "bonus", "jackpot", "you won",
                "you've won", "selected winner", "lucky winner", "claim prize",
                "claim reward", "free money", "cash prize", "gift card", "voucher",
                "coupon", "discount", "offer", "exclusive offer", "limited offer",
                "special offer", "cashback"
            ]
        }
        
        # URL pattern regex
        self.url_pattern = re.compile(
            r'(?:http[s]?://|www\.|bit\.ly|tinyurl\.com|goo\.gl|t\.co|ow\.ly|short\.link)',
            re.IGNORECASE
        )
        
        # Brand to official domain mapping
        self.brand_domains = {
            "sbi": ["sbi.co.in", "onlinesbi.com", "onlinesbi.sbi"],
            "hdfc": ["hdfcbank.com", "hdfc.com"],
            "icici": ["icicibank.com", "icici.com"],
            "axis": ["axisbank.com", "axisbank.co.in"],
            "amazon": ["amazon.in", "amazon.com"],
            "paypal": ["paypal.com", "paypal.in"],
            "paytm": ["paytm.com", "paytm.in"],
            "flipkart": ["flipkart.com"],
            "rbi": ["rbi.org.in"],
            "kotak": ["kotak.com", "kotakbank.com"],
            "google": ["google.com", "google.co.in"],
            "microsoft": ["microsoft.com", "live.com"],
            "facebook": ["facebook.com", "fb.com"],
            "whatsapp": ["whatsapp.com"]
        }
    
    def analyze(self, message: str) -> RuleResult:
        """
        Analyze a message for suspicious patterns and calculate a rule-based risk score.
        
        Args:
            message: The message text to analyze
            
        Returns:
            RuleResult containing:
            - rule_score: Calculated score (0-100) based on triggered patterns
            - triggered_keywords: Dictionary mapping categories to detected keywords
            - pattern_weights: Dictionary mapping categories to their weight contributions
        """
        logger.info(f"Starting rule-based analysis: message_length={len(message)}")
        
        message_lower = message.lower()
        triggered_keywords: Dict[str, List[str]] = {}
        active_pattern_weights: Dict[str, float] = {}
        
        # Check keyword-based patterns
        for category, keywords in self.patterns.items():
            detected = []
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    detected.append(keyword)
            
            if detected:
                triggered_keywords[category] = detected
                active_pattern_weights[category] = self.pattern_weights[category]
                logger.info(
                    f"Pattern triggered: category={category}, "
                    f"keywords={detected}, weight={self.pattern_weights[category]}"
                )
        
        # Check for URLs
        if self.url_pattern.search(message):
            triggered_keywords["urls"] = ["URL detected"]
            active_pattern_weights["urls"] = self.pattern_weights["urls"]
            logger.info(f"URL pattern detected: weight={self.pattern_weights['urls']}")
        
        # Check for brand-domain mismatch
        if self._detect_brand_mismatch(message):
            triggered_keywords["brand_mismatch"] = ["Brand-domain mismatch detected"]
            active_pattern_weights["brand_mismatch"] = self.pattern_weights["brand_mismatch"]
            logger.warning(
                f"Brand-domain mismatch detected: weight={self.pattern_weights['brand_mismatch']}"
            )
        
        # Calculate rule score: sum of all triggered pattern weights, capped at 100
        rule_score = min(100.0, sum(active_pattern_weights.values()))
        
        logger.info(
            f"Rule analysis complete: rule_score={rule_score:.2f}, "
            f"patterns_triggered={len(triggered_keywords)}, "
            f"total_weight={sum(active_pattern_weights.values()):.2f}"
        )
        
        return RuleResult(
            rule_score=rule_score,
            triggered_keywords=triggered_keywords,
            pattern_weights=active_pattern_weights
        )
    
    def _detect_brand_mismatch(self, message: str) -> bool:
        """
        Detect if a message contains a brand name but URLs with mismatched domains.
        
        Args:
            message: The message text to analyze
            
        Returns:
            True if brand-domain mismatch is detected, False otherwise
        """
        message_lower = message.lower()
        
        # Extract all URLs from the message
        urls = self._extract_urls(message)
        
        if not urls:
            return False
        
        # Check if any brand is mentioned
        for brand, official_domains in self.brand_domains.items():
            if brand in message_lower:
                # Brand is mentioned, check if any URL matches official domains
                has_official_domain = False
                for url in urls:
                    url_lower = url.lower()
                    for domain in official_domains:
                        if domain in url_lower:
                            has_official_domain = True
                            break
                    if has_official_domain:
                        break
                
                # If brand is mentioned but no official domain found, it's a mismatch
                if not has_official_domain:
                    return True
        
        return False
    
    def _extract_urls(self, message: str) -> List[str]:
        """
        Extract all URLs from a message.
        
        Args:
            message: The message text to extract URLs from
            
        Returns:
            List of extracted URLs
        """
        # More comprehensive URL extraction pattern
        url_regex = re.compile(
            r'(?:http[s]?://[^\s]+|www\.[^\s]+|'
            r'bit\.ly/[^\s]+|tinyurl\.com/[^\s]+|'
            r'goo\.gl/[^\s]+|t\.co/[^\s]+|'
            r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)',
            re.IGNORECASE
        )
        
        urls = url_regex.findall(message)
        return urls
