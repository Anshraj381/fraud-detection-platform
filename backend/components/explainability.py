"""
Explainability Module for the Intelligent Digital Fraud Awareness and Detection Platform.

This module generates human-readable explanations and safety recommendations based on
fraud detection results.
"""

import logging
from typing import List
from backend.models.data_models import AnalysisResult, Explanation


# Configure logging
logger = logging.getLogger(__name__)


class ExplainabilityModule:
    """
    Generates human-readable explanations and safety recommendations.
    
    This module translates technical fraud detection results into clear, actionable
    information for users, including explanations of why a message was flagged and
    specific safety recommendations based on risk level.
    """
    
    def __init__(self):
        """Initialize the ExplainabilityModule."""
        # Recommendation templates by risk level
        self.high_risk_recommendations = [
            "🚨 DO NOT respond to this message or click any links",
            "🚨 DO NOT share any personal information, passwords, or OTP codes",
            "🚨 Block the sender immediately and report as spam",
            "🚨 Verify sender identity through official channels before taking any action",
            "🚨 Contact your bank directly using official phone numbers if this claims to be from them"
        ]
        
        self.suspicious_recommendations = [
            "⚠️ Verify the sender's identity through official channels before responding",
            "⚠️ Do not click on any links or download attachments without verification",
            "⚠️ Be cautious about sharing any personal or financial information",
            "⚠️ Look for signs of urgency or pressure tactics, which are common in scams"
        ]
        
        self.safe_recommendations = [
            "✅ Always verify sender identity before sharing sensitive information",
            "✅ Be cautious of messages creating urgency or offering unrealistic rewards",
            "✅ Never share OTP codes, even if the request appears legitimate",
            "✅ Keep your awareness high - scammers constantly evolve their tactics"
        ]
    
    def generate_explanation(self, analysis_result: AnalysisResult) -> Explanation:
        """
        Creates explanation and recommendations based on analysis results.
        
        Args:
            analysis_result: Complete analysis results containing scores, risk level,
                           fraud category, and triggered keywords
        
        Returns:
            Explanation object containing:
                - explanation_text: Human-readable explanation of the detection
                - recommendations: List of safety recommendations (3+ for High Risk,
                                 2+ for Suspicious, general tips for Safe)
                - triggered_keywords_summary: Summary of detected suspicious patterns
        """
        logger.info(
            f"Generating explanation: risk_level={analysis_result.risk_level}, "
            f"fraud_category={analysis_result.fraud_category}"
        )
        
        # Generate triggered keywords summary
        triggered_keywords_summary = self._create_keywords_summary(
            analysis_result.triggered_keywords
        )
        
        # Generate explanation text
        explanation_text = self._create_explanation_text(
            analysis_result.risk_level,
            analysis_result.fraud_category,
            analysis_result.final_risk_score,
            analysis_result.ai_probability,
            analysis_result.triggered_keywords
        )
        
        # Generate recommendations based on risk level
        recommendations = self._create_recommendations(
            analysis_result.risk_level,
            analysis_result.fraud_category,
            analysis_result.triggered_keywords
        )
        
        logger.info(
            f"Explanation generated: recommendations_count={len(recommendations)}, "
            f"patterns_detected={len(analysis_result.triggered_keywords)}"
        )
        
        return Explanation(
            explanation_text=explanation_text,
            recommendations=recommendations,
            triggered_keywords_summary=triggered_keywords_summary
        )
    
    def _create_keywords_summary(self, triggered_keywords: dict) -> str:
        """
        Creates a summary of triggered keywords grouped by category.
        
        Args:
            triggered_keywords: Dictionary mapping category names to lists of keywords
        
        Returns:
            Formatted string summarizing all triggered keywords
        """
        if not triggered_keywords:
            return "No suspicious patterns detected."
        
        summary_parts = []
        for category, keywords in triggered_keywords.items():
            if keywords:
                # Format category name for display
                category_display = category.replace('_', ' ').title()
                keywords_str = ", ".join(f'"{kw}"' for kw in keywords)
                summary_parts.append(f"{category_display}: {keywords_str}")
        
        if not summary_parts:
            return "No suspicious patterns detected."
        
        return " | ".join(summary_parts)
    
    def _create_explanation_text(
        self,
        risk_level: str,
        fraud_category: str,
        final_risk_score: float,
        ai_probability: float,
        triggered_keywords: dict
    ) -> str:
        """
        Generates human-readable explanation of the detection.
        
        Args:
            risk_level: Risk classification (Safe/Suspicious/High Risk)
            fraud_category: Detected fraud type
            final_risk_score: Combined risk score (0-100)
            ai_probability: AI model's fraud probability (0-100)
            triggered_keywords: Dictionary of triggered keywords by category
        
        Returns:
            Detailed explanation text
        """
        # Start with risk level assessment
        if risk_level == "High Risk":
            intro = f"⚠️ **HIGH RISK ALERT** - This message has a risk score of {final_risk_score:.1f}/100 and shows strong indicators of fraud."
        elif risk_level == "Suspicious":
            intro = f"⚠️ **SUSPICIOUS** - This message has a risk score of {final_risk_score:.1f}/100 and contains concerning patterns."
        else:
            intro = f"✅ **SAFE** - This message has a low risk score of {final_risk_score:.1f}/100 and appears legitimate."
        
        # Add fraud category information
        if fraud_category and fraud_category != "Other/Unknown":
            category_text = f"\n\n**Detected Category:** {fraud_category}"
        else:
            category_text = ""
        
        # Add AI probability information
        ai_text = f"\n\n**AI Analysis:** The machine learning model assessed this message with a fraud probability of {ai_probability:.1f}%."
        
        # Add triggered patterns explanation
        if triggered_keywords:
            pattern_count = sum(len(keywords) for keywords in triggered_keywords.values())
            patterns_text = f"\n\n**Detected Patterns:** {pattern_count} suspicious pattern(s) were identified in this message."
            
            # Add specific pattern details
            pattern_details = []
            for category, keywords in triggered_keywords.items():
                if keywords:
                    category_display = category.replace('_', ' ').title()
                    pattern_details.append(f"- {category_display}: {len(keywords)} match(es)")
            
            if pattern_details:
                patterns_text += "\n" + "\n".join(pattern_details)
        else:
            patterns_text = "\n\n**Detected Patterns:** No suspicious patterns were identified."
        
        # Combine all parts
        explanation = intro + category_text + ai_text + patterns_text
        
        return explanation
    
    def _create_recommendations(
        self,
        risk_level: str,
        fraud_category: str,
        triggered_keywords: dict
    ) -> List[str]:
        """
        Generates safety recommendations based on risk level and fraud type.
        
        Args:
            risk_level: Risk classification (Safe/Suspicious/High Risk)
            fraud_category: Detected fraud type
            triggered_keywords: Dictionary of triggered keywords by category
        
        Returns:
            List of actionable safety recommendations (minimum 3 for High Risk,
            2 for Suspicious, general tips for Safe)
        """
        recommendations = []
        
        if risk_level == "High Risk":
            # Start with general high-risk recommendations (minimum 3)
            recommendations.extend(self.high_risk_recommendations[:3])
            
            # Add category-specific recommendations
            if fraud_category == "OTP Scam":
                recommendations.append("🚨 Never share OTP codes - legitimate organizations will never ask for them")
            elif fraud_category == "KYC Scam":
                recommendations.append("🚨 Banks never ask for KYC updates via SMS or unofficial channels")
            elif fraud_category == "Bank Impersonation":
                recommendations.append("🚨 Verify any bank communication by calling official customer service numbers")
            elif fraud_category == "Reward/Lottery Scam":
                recommendations.append("🚨 Legitimate lotteries don't require payment or personal details to claim prizes")
            elif fraud_category == "Phishing Link Scam":
                recommendations.append("🚨 Do not click on suspicious links - they may steal your information or install malware")
            
            # Ensure we have at least 3 recommendations
            if len(recommendations) < 3:
                recommendations.extend(self.high_risk_recommendations[3:5])
        
        elif risk_level == "Suspicious":
            # Start with general suspicious recommendations (minimum 2)
            recommendations.extend(self.suspicious_recommendations[:2])
            
            # Add category-specific recommendations
            if "otp_request" in triggered_keywords:
                recommendations.append("⚠️ Be extremely cautious about any OTP sharing requests")
            elif "urls" in triggered_keywords:
                recommendations.append("⚠️ Hover over links to check the actual URL before clicking")
            elif "bank_kyc" in triggered_keywords:
                recommendations.append("⚠️ Contact your bank directly to verify any account-related messages")
            
            # Ensure we have at least 2 recommendations
            if len(recommendations) < 2:
                recommendations.extend(self.suspicious_recommendations[2:4])
        
        else:  # Safe
            # Provide general awareness tips
            recommendations.extend(self.safe_recommendations)
        
        return recommendations
