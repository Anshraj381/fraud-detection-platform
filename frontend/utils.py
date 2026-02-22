"""
Utility functions for the Streamlit frontend.

This module provides helper functions for formatting and displaying
fraud detection results in the user interface.
"""

from typing import Dict, List

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def inject_custom_css():
    """Inject custom CSS for modern styling and animations."""
    if not HAS_STREAMLIT:
        return
    
    st.markdown(
        """
        <style>
        /* Main header styling */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .main-title {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            text-align: center;
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            text-align: center;
            margin-top: 0.5rem;
        }
        
        /* Score cards */
        .score-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-bottom: 1rem;
        }
        
        .score-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .score-card.green { border-left-color: #28a745; }
        .score-card.orange { border-left-color: #ffc107; }
        .score-card.red { border-left-color: #dc3545; }
        .score-card.blue { border-left-color: #007bff; }
        .score-card.purple { border-left-color: #6f42c1; }
        
        .card-title {
            font-size: 0.9rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .card-value {
            font-size: 2rem;
            font-weight: 700;
            color: #212529;
            margin: 0.5rem 0;
        }
        
        .card-subtitle {
            font-size: 0.85rem;
            color: #6c757d;
        }
        
        /* Risk gauge */
        .risk-gauge {
            text-align: center;
            padding: 2rem;
            margin: 2rem 0;
        }
        
        .gauge-container {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto;
        }
        
        .gauge-circle {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: conic-gradient(
                from 0deg,
                #28a745 0deg,
                #ffc107 120deg,
                #dc3545 240deg,
                #dc3545 360deg
            );
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .gauge-inner {
            width: 85%;
            height: 85%;
            border-radius: 50%;
            background: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .gauge-score {
            font-size: 3rem;
            font-weight: 700;
            color: #212529;
        }
        
        .gauge-label {
            font-size: 1rem;
            color: #6c757d;
            margin-top: 0.5rem;
        }
        
        /* Awareness card */
        .awareness-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .score-display {
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
        }
        
        .score-max {
            font-size: 1.5rem;
            opacity: 0.8;
        }
        
        .level-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        
        /* Level info */
        .level-info {
            padding: 0.5rem 0;
        }
        
        .level-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .level-label {
            font-weight: 600;
            color: #495057;
        }
        
        .level-range {
            color: #6c757d;
        }
        
        /* Character counter */
        .char-counter {
            margin: 0.5rem 0 1rem 0;
            font-size: 0.9rem;
        }
        
        .char-progress {
            width: 100%;
            height: 4px;
            background: #e9ecef;
            border-radius: 2px;
            margin-top: 0.25rem;
            overflow: hidden;
        }
        
        .char-progress-bar {
            height: 100%;
            transition: width 0.3s ease, background-color 0.3s ease;
        }
        
        /* Keyword badges */
        .keyword-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            margin: 0.25rem;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 500;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            transition: all 0.2s;
        }
        
        .keyword-badge:hover {
            background: #e9ecef;
            transform: scale(1.05);
        }
        
        .keyword-category {
            font-weight: 700;
            color: #495057;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        /* Explanation box */
        .explanation-box {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .explanation-box p {
            margin: 0;
            color: #495057;
            line-height: 1.6;
        }
        
        /* Recommendation cards */
        .recommendation-card {
            display: flex;
            align-items: flex-start;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        
        .recommendation-card:hover {
            border-color: #007bff;
            box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
        }
        
        .rec-number {
            flex-shrink: 0;
            width: 30px;
            height: 30px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-right: 1rem;
        }
        
        .rec-text {
            flex: 1;
            color: #495057;
            line-height: 1.6;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #6c757d;
            padding: 2rem 0;
        }
        
        .footer p {
            margin: 0.25rem 0;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .score-card, .recommendation-card {
            animation: fadeIn 0.3s ease-out;
        }
        
        /* Sample message buttons */
        .stButton button {
            transition: all 0.2s;
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        </style>
        """,
        unsafe_allow_html=True
    )


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
        return "<p style='color: #6c757d;'>No suspicious keywords detected</p>"
    
    html_parts = []
    
    # Category display names
    category_names = {
        "urgency": "Urgency Indicators",
        "otp_request": "OTP Request",
        "bank_kyc": "Bank/KYC Related",
        "reward_scam": "Reward/Lottery",
        "url": "URL Detected",
        "brand_mismatch": "Brand Mismatch"
    }
    
    for category, keywords in triggered_keywords.items():
        if keywords:
            display_name = category_names.get(category, category.replace("_", " ").title())
            html_parts.append(f'<div class="keyword-category">{display_name}</div>')
            html_parts.append('<div>')
            
            # Create badges for each keyword
            for keyword in keywords:
                html_parts.append(f'<span class="keyword-badge">{keyword}</span>')
            
            html_parts.append('</div>')
    
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


def get_awareness_level_name(awareness_level: str) -> str:
    """
    Get display name for awareness level.
    
    Args:
        awareness_level: Awareness level string
        
    Returns:
        Display name for the awareness level
    """
    return awareness_level


def get_category_display_name(fraud_category: str) -> str:
    """
    Get display name for fraud category.
    
    Args:
        fraud_category: Fraud category string
        
    Returns:
        Display name for the fraud category
    """
    return fraud_category


def create_risk_gauge(risk_score: float, risk_level: str) -> str:
    """
    Create an animated risk gauge visualization.
    
    Args:
        risk_score: Risk score (0-100)
        risk_level: Risk level string
        
    Returns:
        HTML string for risk gauge
    """
    return f"""
    <div class="risk-gauge">
        <div class="gauge-container">
            <div class="gauge-circle">
                <div class="gauge-inner">
                    <div class="gauge-score">{risk_score:.0f}</div>
                    <div class="gauge-label">{risk_level}</div>
                </div>
            </div>
        </div>
    </div>
    """


def create_score_card(title: str, value: str, subtitle: str, color: str) -> str:
    """
    Create a score card with color coding.
    
    Args:
        title: Card title
        value: Main value to display
        subtitle: Subtitle text
        color: Color theme (green, orange, red, blue, purple)
        
    Returns:
        HTML string for score card
    """
    return f"""
    <div class="score-card {color}">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        <div class="card-subtitle">{subtitle}</div>
    </div>
    """


def get_sample_messages() -> List[Dict[str, str]]:
    """
    Get sample messages for quick testing.
    
    Returns:
        List of sample message dictionaries
    """
    return [
        {
            "label": "High Risk: OTP Scam",
            "preview": "Urgent OTP request from fake bank",
            "message": "URGENT: Your bank account will be blocked. Share OTP 123456 immediately to verify your identity. Call us at 9876543210."
        },
        {
            "label": "High Risk: Lottery Scam",
            "preview": "Fake lottery winning notification",
            "message": "Congratulations! You have won Rs 25 lakhs in lucky draw. Click here to claim: http://bit.ly/fake-lottery. Share your bank details now!"
        },
        {
            "label": "Suspicious: KYC Update",
            "preview": "Suspicious KYC update request",
            "message": "Dear customer, your KYC documents are pending. Update now to avoid account suspension. Visit our website and submit documents."
        },
        {
            "label": "Safe: Legitimate OTP",
            "preview": "Normal OTP from known service",
            "message": "Your OTP for login is 456789. Valid for 10 minutes. Do not share this OTP with anyone."
        },
        {
            "label": "High Risk: Phishing Link",
            "preview": "Phishing attempt with suspicious URL",
            "message": "Your package is waiting! Track your delivery here: http://amaz0n-delivery.com/track?id=12345. Enter your card details to confirm."
        },
        {
            "label": "Suspicious: Prize Winner",
            "preview": "Suspicious prize notification",
            "message": "You are selected as lucky winner of iPhone 15 Pro. Claim your prize by paying Rs 500 processing fee. Limited time offer!"
        }
    ]
