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
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from frontend.utils import (
    get_risk_color,
    format_keywords,
    format_recommendations,
    get_awareness_level_name,
    get_category_display_name,
    inject_custom_css,
    create_risk_gauge,
    create_score_card,
    get_sample_messages
)


# Configuration
API_URL = "http://localhost:8000"
MAX_MESSAGE_LENGTH = 5000


# Page configuration
st.set_page_config(
    page_title="Fraud Detection Platform",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for modern styling
inject_custom_css()


def display_header():
    """Display the application header and description."""
    st.markdown(
        """
        <div class="header-container">
            <h1 class="main-title">Intelligent Digital Fraud Detection Platform</h1>
            <p class="subtitle">Analyze suspicious SMS, WhatsApp messages, and call transcripts to detect potential fraud using AI-powered detection.</p>
        </div>
        """,
        unsafe_allow_html=True
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
        st.markdown("### Your Awareness Score")
        
        if awareness_score is not None and awareness_level is not None:
            level_name = get_awareness_level_name(awareness_level)
            
            # Create animated progress bar
            st.markdown(
                f"""
                <div class="awareness-card">
                    <div class="score-display">{awareness_score:.1f}<span class="score-max">/100</span></div>
                    <div class="level-badge level-{awareness_level.lower().replace(' ', '-')}">{level_name}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Animated progress bar
            st.progress(awareness_score / 100)
            
            # Level descriptions in expander
            with st.expander("View All Levels"):
                st.markdown(
                    """
                    <div class="level-info">
                        <div class="level-item">
                            <span class="level-label">Beginner</span>
                            <span class="level-range">0-40</span>
                        </div>
                        <div class="level-item">
                            <span class="level-label">Improving</span>
                            <span class="level-range">41-60</span>
                        </div>
                        <div class="level-item">
                            <span class="level-label">Aware</span>
                            <span class="level-range">61-80</span>
                        </div>
                        <div class="level-item">
                            <span class="level-label">Highly Aware</span>
                            <span class="level-range">81-100</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Analyze messages to track your fraud awareness improvement!")
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("View Analytics Dashboard", use_container_width=True):
            st.switch_page("pages/analytics.py")
        
        if st.button("Clear History", use_container_width=True):
            st.session_state.clear()
            st.rerun()


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
            "**Cannot connect to backend server**  \n"
            "Please ensure the API is running on http://localhost:8000"
        )
        return None
    
    except requests.exceptions.Timeout:
        st.error(
            "**Request timed out**  \n"
            "The analysis is taking too long. Please try again."
        )
        return None
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_detail = e.response.json().get("detail", "Invalid input")
            st.error(f"**Validation Error:** {error_detail}")
        elif e.response.status_code == 500:
            error_detail = e.response.json().get("detail", "Internal server error")
            st.error(f"**Server Error:** {error_detail}")
        else:
            st.error(f"**HTTP Error {e.response.status_code}:** {str(e)}")
        return None
    
    except Exception as e:
        st.error(f"**Unexpected Error:** {str(e)}")
        return None


def display_results(result: dict):
    """
    Display analysis results in a formatted layout with tabs and interactive elements.
    
    Args:
        result: Analysis results dictionary from backend
    """
    risk_score = result.get("risk_score", 0)
    risk_level = result.get("risk_level", "Unknown")
    fraud_category = result.get("fraud_category", "Unknown")
    ai_probability = result.get("ai_probability", 0)
    rule_score = result.get("rule_score", 0)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Summary", "Detailed Analysis", "Recommendations"])
    
    with tab1:
        st.markdown("## Analysis Summary")
        
        # Risk gauge visualization
        risk_gauge_html = create_risk_gauge(risk_score, risk_level)
        st.markdown(risk_gauge_html, unsafe_allow_html=True)
        
        # Score cards in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            card_html = create_score_card(
                "Risk Score",
                f"{risk_score:.1f}",
                "out of 100",
                get_risk_color(risk_level)
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        with col2:
            category_display = get_category_display_name(fraud_category)
            card_html = create_score_card(
                "Fraud Category",
                category_display,
                fraud_category,
                "blue"
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        with col3:
            card_html = create_score_card(
                "AI Confidence",
                f"{ai_probability:.1f}%",
                f"Rule Score: {rule_score:.1f}",
                "purple"
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        # Risk level alert
        st.markdown("<br>", unsafe_allow_html=True)
        if risk_level == "Safe":
            st.success(f"**Status:** {risk_level} - This message appears to be legitimate.")
        elif risk_level == "Suspicious":
            st.warning(f"**Status:** {risk_level} - Exercise caution with this message.")
        else:  # High Risk
            st.error(f"**Status:** {risk_level} - This message shows strong fraud indicators!")
    
    with tab2:
        st.markdown("## Detailed Analysis")
        
        # Detected Patterns Section
        with st.expander("Detected Patterns & Keywords", expanded=True):
            triggered_keywords = result.get("triggered_keywords", {})
            keywords_html = format_keywords(triggered_keywords)
            st.markdown(keywords_html, unsafe_allow_html=True)
        
        # AI Explanation Section
        with st.expander("AI Explanation", expanded=True):
            explanation = result.get("explanation", "No explanation available")
            st.markdown(
                f"""
                <div class="explanation-box">
                    <p>{explanation}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Technical Details
        with st.expander("Technical Details"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("AI Probability", f"{ai_probability:.2f}%")
                st.metric("Rule-Based Score", f"{rule_score:.2f}")
            with col2:
                st.metric("Combined Risk Score", f"{risk_score:.2f}")
                st.metric("Risk Level", risk_level)
    
    with tab3:
        st.markdown("## Safety Recommendations")
        
        recommendations = result.get("recommendations", [])
        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                with st.container():
                    st.markdown(
                        f"""
                        <div class="recommendation-card">
                            <div class="rec-number">{idx}</div>
                            <div class="rec-text">{rec}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("No specific recommendations at this time.")
        
        # Quick tips section
        with st.expander("General Fraud Prevention Tips"):
            st.markdown(
                """
                - Never share OTP codes with anyone, including bank representatives
                - Verify sender identity through official channels before responding
                - Be skeptical of urgent requests for personal or financial information
                - Check URLs carefully before clicking - look for misspellings or suspicious domains
                - Contact your bank directly using official numbers if you receive suspicious messages
                - Report suspected fraud to relevant authorities
                """
            )
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Analyze Another Message", use_container_width=True):
            st.rerun()
    
    with col2:
        # Export results as JSON
        if st.button("Export Results", use_container_width=True):
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="fraud_analysis_results.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col3:
        if st.button("Copy Summary", use_container_width=True):
            summary = f"Risk Score: {risk_score:.1f}/100 | Level: {risk_level} | Category: {fraud_category}"
            st.code(summary)
            st.info("Summary displayed above - copy manually")
    
    with col4:
        if st.button("View Analytics", use_container_width=True):
            st.switch_page("pages/analytics.py")
    
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
    
    # Sample messages section
    with st.expander("Try Sample Messages", expanded=False):
        st.markdown("Click any sample message below to analyze it:")
        samples = get_sample_messages()
        
        cols = st.columns(2)
        for idx, sample in enumerate(samples):
            with cols[idx % 2]:
                if st.button(
                    sample["label"],
                    key=f"sample_{idx}",
                    use_container_width=True,
                    help=sample["preview"]
                ):
                    st.session_state["sample_message"] = sample["message"]
                    st.rerun()
    
    # Message input section
    st.markdown("## Analyze a Message")
    st.markdown(
        "Paste a suspicious SMS, WhatsApp message, or call transcript below to check for fraud indicators."
    )
    
    # Check if sample message was selected
    default_message = st.session_state.pop("sample_message", "")
    
    # Text area for message input
    message = st.text_area(
        label="Message Content",
        placeholder="Enter the suspicious message here...",
        height=150,
        max_chars=MAX_MESSAGE_LENGTH,
        help=f"Maximum {MAX_MESSAGE_LENGTH} characters",
        value=default_message
    )
    
    # Character counter with visual feedback
    char_count = len(message)
    char_percentage = (char_count / MAX_MESSAGE_LENGTH) * 100
    
    if char_percentage < 50:
        counter_color = "#28a745"
    elif char_percentage < 80:
        counter_color = "#ffc107"
    else:
        counter_color = "#dc3545"
    
    st.markdown(
        f"""
        <div class="char-counter">
            <span style="color: {counter_color}; font-weight: bold;">{char_count}</span> / {MAX_MESSAGE_LENGTH} characters
            <div class="char-progress">
                <div class="char-progress-bar" style="width: {min(char_percentage, 100)}%; background-color: {counter_color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        clear_button = st.button("Clear", use_container_width=True)
        if clear_button:
            st.rerun()
    
    with col2:
        analyze_button = st.button(
            "Analyze Message",
            type="primary",
            use_container_width=True
        )
    
    with col3:
        help_button = st.button("Help", use_container_width=True)
        if help_button:
            st.info(
                "Enter or paste a message you want to analyze for fraud indicators. "
                "The system will check for suspicious patterns, keywords, and provide a risk assessment."
            )
    
    # Process analysis
    if analyze_button:
        if not message or not message.strip():
            st.warning("Please enter a message to analyze.")
        elif char_count > MAX_MESSAGE_LENGTH:
            st.error(f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters.")
        else:
            # Show loading spinner with progress
            with st.spinner("Analyzing message..."):
                result = analyze_message(message)
            
            if result:
                st.success("Analysis complete!")
                st.divider()
                display_results(result)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            <p><strong>Intelligent Digital Fraud Awareness and Detection Platform</strong></p>
            <p>All processing is done locally. Your data never leaves your device.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
