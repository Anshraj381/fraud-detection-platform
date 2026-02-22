"""
Streamlit frontend for the Intelligent Digital Fraud Awareness and Detection Platform.

This module provides the main user interface for analyzing suspicious messages
and viewing fraud detection results.
"""

import streamlit as st
import requests
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from frontend.utils import (
    get_risk_color,
    format_keywords,
    format_recommendations,
    get_awareness_emoji,
    get_category_emoji
)


# Configuration
API_URL = "http://localhost:8000"
MAX_MESSAGE_LENGTH = 5000


# Page configuration
st.set_page_config(
    page_title="Fraud Detection Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def display_header():
    """Display the application header and description."""
    st.title("🛡️ Intelligent Digital Fraud Detection Platform")
    st.markdown(
        """
        Analyze suspicious SMS, WhatsApp messages, and call transcripts to detect potential fraud.
        This system uses AI and rule-based detection to identify scam patterns and provide safety recommendations.
        """
    )
    st.divider()


def display_awareness_sidebar(awareness_score: Optional[float] = None, 
                              awareness_level: Optional[str] = None):
    """
    Display awareness score in the sidebar.
    
    Args:
        awareness_score: Current awareness score (0-100)
        awareness_level: Current awareness level
    """
    with st.sidebar:
        st.header("📊 Your Awareness")
        
        if awareness_score is not None and awareness_level is not None:
            emoji = get_awareness_emoji(awareness_level)
            st.metric(
                label="Awareness Score",
                value=f"{awareness_score:.1f}/100"
            )
            st.markdown(f"### {emoji} {awareness_level}")
            
            # Progress bar
            st.progress(awareness_score / 100)
            
            # Level descriptions
            st.markdown("---")
            st.markdown("**Awareness Levels:**")
            st.markdown("🌱 Beginner (0-40)")
            st.markdown("📈 Improving (41-60)")
            st.markdown("🎯 Aware (61-80)")
            st.markdown("🏆 Highly Aware (81-100)")
        else:
            st.info("Analyze messages to track your fraud awareness improvement!")
        
        st.markdown("---")
        st.markdown("### 📈 [View Analytics Dashboard](analytics)")


def analyze_message(message: str) -> Optional[dict]:
    """
    Send message to backend for analysis.
    
    Args:
        message: Message text to analyze
        
    Returns:
        Analysis results dictionary or None if error occurs
    """
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={"message": message},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        st.error(
            "❌ **Cannot connect to backend server**  \n"
            "Please ensure the API is running on http://localhost:8000"
        )
        return None
    
    except requests.exceptions.Timeout:
        st.error(
            "⏱️ **Request timed out**  \n"
            "The analysis is taking too long. Please try again."
        )
        return None
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_detail = e.response.json().get("detail", "Invalid input")
            st.error(f"❌ **Validation Error:** {error_detail}")
        elif e.response.status_code == 500:
            error_detail = e.response.json().get("detail", "Internal server error")
            st.error(f"❌ **Server Error:** {error_detail}")
        else:
            st.error(f"❌ **HTTP Error {e.response.status_code}:** {str(e)}")
        return None
    
    except Exception as e:
        st.error(f"❌ **Unexpected Error:** {str(e)}")
        return None


def display_results(result: dict):
    """
    Display analysis results in a formatted layout.
    
    Args:
        result: Analysis results dictionary from backend
    """
    # Risk Score Section
    st.markdown("## 📊 Analysis Results")
    
    risk_score = result.get("risk_score", 0)
    risk_level = result.get("risk_level", "Unknown")
    fraud_category = result.get("fraud_category", "Unknown")
    
    # Color-coded risk display
    risk_color = get_risk_color(risk_level)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Risk Score",
            value=f"{risk_score:.1f}/100"
        )
        if risk_level == "Safe":
            st.success(f"✅ **{risk_level}**")
        elif risk_level == "Suspicious":
            st.warning(f"⚠️ **{risk_level}**")
        else:  # High Risk
            st.error(f"🚨 **{risk_level}**")
    
    with col2:
        category_emoji = get_category_emoji(fraud_category)
        st.metric(
            label="Fraud Category",
            value=fraud_category
        )
        st.markdown(f"### {category_emoji}")
    
    with col3:
        ai_probability = result.get("ai_probability", 0)
        rule_score = result.get("rule_score", 0)
        st.metric(
            label="AI Confidence",
            value=f"{ai_probability:.1f}%"
        )
        st.caption(f"Rule Score: {rule_score:.1f}")
    
    st.divider()
    
    # Triggered Keywords Section
    st.markdown("### 🔍 Detected Patterns")
    triggered_keywords = result.get("triggered_keywords", {})
    keywords_html = format_keywords(triggered_keywords)
    st.markdown(keywords_html)
    
    st.divider()
    
    # Explanation Section
    st.markdown("### 💡 AI Explanation")
    explanation = result.get("explanation", "No explanation available")
    st.info(explanation)
    
    st.divider()
    
    # Recommendations Section
    st.markdown("### 🛡️ Safety Recommendations")
    recommendations = result.get("recommendations", [])
    recommendations_text = format_recommendations(recommendations)
    st.markdown(recommendations_text)
    
    # Update sidebar with awareness score
    awareness_score = result.get("awareness_score")
    awareness_level = result.get("awareness_level")
    if awareness_score is not None and awareness_level is not None:
        st.session_state["awareness_score"] = awareness_score
        st.session_state["awareness_level"] = awareness_level


def main():
    """Main application function."""
    # Display header
    display_header()
    
    # Display sidebar with awareness score
    awareness_score = st.session_state.get("awareness_score")
    awareness_level = st.session_state.get("awareness_level")
    display_awareness_sidebar(awareness_score, awareness_level)
    
    # Message input section
    st.markdown("## 📝 Analyze a Message")
    st.markdown(
        "Paste a suspicious SMS, WhatsApp message, or call transcript below to check for fraud indicators."
    )
    
    # Text area for message input
    message = st.text_area(
        label="Message Content",
        placeholder="Enter the suspicious message here...",
        height=150,
        max_chars=MAX_MESSAGE_LENGTH,
        help=f"Maximum {MAX_MESSAGE_LENGTH} characters"
    )
    
    # Character counter
    char_count = len(message)
    char_color = "red" if char_count > MAX_MESSAGE_LENGTH else "gray"
    st.caption(f":{char_color}[{char_count}/{MAX_MESSAGE_LENGTH} characters]")
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Analyze Message",
            type="primary",
            use_container_width=True
        )
    
    # Process analysis
    if analyze_button:
        if not message or not message.strip():
            st.warning("⚠️ Please enter a message to analyze.")
        elif char_count > MAX_MESSAGE_LENGTH:
            st.error(f"❌ Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters.")
        else:
            # Show loading spinner
            with st.spinner("🔄 Analyzing message..."):
                result = analyze_message(message)
            
            if result:
                st.success("✅ Analysis complete!")
                st.divider()
                display_results(result)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <p>🛡️ Intelligent Digital Fraud Awareness and Detection Platform</p>
            <p>All processing is done locally. Your data never leaves your device.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
