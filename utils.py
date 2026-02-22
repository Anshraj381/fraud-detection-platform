"""
Utility functions for the Streamlit frontend.

This module provides helper functions for formatting and displaying
fraud detection results in the user interface.
"""

from typing import Dict, List


def get_risk_color(risk_level: str) -> str:
    """
    Get color code for risk level display.
    
    Args:
        risk_level: Risk level string ("Safe", "Suspicious", or "High Risk")
        
    Returns:
        Color code for Streamlit display (green, yellow, or red)
    """
    color_map = {
        "Safe": "green",
        "Suspicious": "orange",
        "High Risk": "red"
    }
    return color_map.get(risk_level, "gray")


def format_keywords(triggered_keywords: Dict[str, List[str]]) -> str:
    """
    Format triggered keywords for display as badges/chips.
    
    Args:
        triggered_keywords: Dictionary mapping category to list of keywords
        
    Returns:
        Formatted HTML string with styled keyword badges
    """
    if not triggered_keywords:
        return "No suspicious keywords detected"
    
    html_parts = []
    
    # Category display names
    category_names = {
        "urgency": "⚠️ Urgency",
        "otp_request": "🔐 OTP Request",
        "bank_kyc": "🏦 Bank/KYC",
        "reward_scam": "🎁 Reward/Lottery",
        "url": "🔗 URL",
        "brand_mismatch": "⚠️ Brand Mismatch"
    }
    
    for category, keywords in triggered_keywords.items():
        if keywords:
            display_name = category_names.get(category, category.replace("_", " ").title())
            html_parts.append(f"**{display_name}:** ")
            
            # Create badges for each keyword
            badges = [f"`{keyword}`" for keyword in keywords]
            html_parts.append(" ".join(badges))
            html_parts.append("  \n")  # Line break
    
    return "".join(html_parts)


def format_recommendations(recommendations: List[str]) -> str:
    """
    Format safety recommendations as a bulleted list.
    
    Args:
        recommendations: List of recommendation strings
        
    Returns:
        Formatted markdown string with bulleted recommendations
    """
    if not recommendations:
        return "No specific recommendations at this time."
    
    formatted = []
    for rec in recommendations:
        formatted.append(f"- {rec}")
    
    return "\n".join(formatted)


def get_awareness_emoji(awareness_level: str) -> str:
    """
    Get emoji for awareness level display.
    
    Args:
        awareness_level: Awareness level string
        
    Returns:
        Emoji representing the awareness level
    """
    emoji_map = {
        "Beginner": "🌱",
        "Improving": "📈",
        "Aware": "🎯",
        "Highly Aware": "🏆"
    }
    return emoji_map.get(awareness_level, "📊")


def get_category_emoji(fraud_category: str) -> str:
    """
    Get emoji for fraud category display.
    
    Args:
        fraud_category: Fraud category string
        
    Returns:
        Emoji representing the fraud category
    """
    emoji_map = {
        "OTP Scam": "🔐",
        "KYC Scam": "📋",
        "Bank Impersonation": "🏦",
        "Reward/Lottery Scam": "🎁",
        "Phishing Link Scam": "🔗",
        "Other/Unknown": "❓"
    }
    return emoji_map.get(fraud_category, "⚠️")
