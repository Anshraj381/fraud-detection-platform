"""
Data models for the Intelligent Digital Fraud Awareness and Detection Platform.

This module defines all dataclasses used throughout the system for structured data exchange
between components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime


@dataclass
class RuleResult:
    """
    Result from Rule Engine analysis.
    
    Attributes:
        rule_score: Calculated rule-based score (0-100)
        triggered_keywords: Dictionary mapping category names to lists of triggered keywords
        pattern_weights: Dictionary mapping category names to their weight contributions
    """
    rule_score: float
    triggered_keywords: Dict[str, List[str]]
    pattern_weights: Dict[str, float]


@dataclass
class RiskAssessment:
    """
    Final risk assessment combining rule-based and AI scores.
    
    Attributes:
        final_score: Combined risk score (0-100)
        risk_level: Classification label ("Safe" | "Suspicious" | "High Risk")
    """
    final_score: float
    risk_level: str


@dataclass
class Explanation:
    """
    Human-readable explanation of fraud detection results.
    
    Attributes:
        explanation_text: Detailed explanation of why the message was flagged
        recommendations: List of actionable safety recommendations
        triggered_keywords_summary: Summary of detected suspicious patterns
    """
    explanation_text: str
    recommendations: List[str]
    triggered_keywords_summary: str


@dataclass
class AwarenessScore:
    """
    User awareness tracking metrics.
    
    Attributes:
        score: Calculated awareness score (0-100)
        level: Classification label ("Beginner" | "Improving" | "Aware" | "Highly Aware")
        high_risk_percentage: Percentage of high-risk messages analyzed
        usage_frequency_factor: Factor based on total usage count
    """
    score: float
    level: str
    high_risk_percentage: float
    usage_frequency_factor: float


@dataclass
class AnalysisResult:
    """
    Complete analysis result containing all detection outputs.
    
    Attributes:
        message_text: Original message that was analyzed
        rule_score: Score from rule-based detection (0-100)
        ai_probability: Fraud probability from ML model (0-100)
        final_risk_score: Combined risk score (0-100)
        risk_level: Risk classification ("Safe" | "Suspicious" | "High Risk")
        fraud_category: Detected fraud type
        triggered_keywords: Dictionary of triggered keywords by category
        explanation: Human-readable explanation text
        recommendations: List of safety recommendations
        awareness_score: Current user awareness score (0-100)
        awareness_level: User awareness level classification
        timestamp: When the analysis was performed
    """
    message_text: str
    rule_score: float
    ai_probability: float
    final_risk_score: float
    risk_level: str
    fraud_category: str
    triggered_keywords: Dict[str, List[str]]
    explanation: str
    recommendations: List[str]
    awareness_score: float
    awareness_level: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AnalyticsData:
    """
    Aggregated analytics data for dashboard visualization.
    
    Attributes:
        total_messages: Total number of messages analyzed
        risk_distribution: Count of messages by risk level
        category_distribution: Count of messages by fraud category
        average_risk_score: Mean risk score across all analyses
        top_keywords: List of (keyword, count) tuples for most common keywords
        risk_trend: List of dictionaries containing timestamp and score pairs for trend analysis
    """
    total_messages: int
    risk_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    average_risk_score: float
    top_keywords: List[tuple]  # List of (keyword, count) tuples
    risk_trend: List[Dict[str, Any]]  # List of {timestamp, score} dictionaries
