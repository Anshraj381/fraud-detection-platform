"""
Analytics Dashboard for the Intelligent Digital Fraud Awareness and Detection Platform.

This module provides a comprehensive analytics dashboard displaying:
- Total messages analyzed
- Risk distribution
- Fraud category distribution
- Risk score trends
- Top keywords
- User awareness metrics
- History management
"""

import streamlit as st
import requests
import pandas as pd
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from frontend.utils import get_awareness_emoji


# Configuration
API_URL = "http://localhost:8000"


# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard - Fraud Detection",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def fetch_analytics() -> Optional[dict]:
    """
    Fetch analytics data from backend.
    
    Returns:
        Analytics data dictionary or None if error occurs
    """
    try:
        response = requests.get(
            f"{API_URL}/analytics",
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
            "Please try again."
        )
        return None
    
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ **HTTP Error {e.response.status_code}:** {str(e)}")
        return None
    
    except Exception as e:
        st.error(f"❌ **Unexpected Error:** {str(e)}")
        return None


def clear_history() -> bool:
    """
    Clear all analysis history from database.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.delete(
            f"{API_URL}/history",
            json={"confirm": True},
            timeout=10
        )
        response.raise_for_status()
        return True
    
    except Exception as e:
        st.error(f"❌ **Failed to clear history:** {str(e)}")
        return False


def display_header():
    """Display the dashboard header."""
    st.title("📊 Analytics Dashboard")
    st.markdown(
        """
        View comprehensive statistics and trends from your fraud detection analyses.
        Track your awareness improvement and identify common fraud patterns.
        """
    )
    st.divider()


def display_key_metrics(analytics: dict):
    """
    Display key metrics in a row of columns.
    
    Args:
        analytics: Analytics data dictionary
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_messages = analytics.get("total_messages", 0)
        st.metric(
            label="📨 Total Messages Analyzed",
            value=total_messages
        )
    
    with col2:
        avg_risk_score = analytics.get("average_risk_score", 0)
        st.metric(
            label="📊 Average Risk Score",
            value=f"{avg_risk_score:.1f}/100"
        )
    
    with col3:
        # Calculate awareness from session state or show placeholder
        awareness_score = st.session_state.get("awareness_score", 0)
        awareness_level = st.session_state.get("awareness_level", "Beginner")
        emoji = get_awareness_emoji(awareness_level)
        st.metric(
            label=f"{emoji} Awareness Level",
            value=awareness_level,
            delta=f"{awareness_score:.1f}/100"
        )


def display_risk_distribution(analytics: dict):
    """
    Display risk distribution as a pie chart.
    
    Args:
        analytics: Analytics data dictionary
    """
    st.markdown("### 🎯 Risk Distribution")
    
    risk_dist = analytics.get("risk_distribution", {})
    
    if not risk_dist or sum(risk_dist.values()) == 0:
        st.info("No data available yet. Analyze some messages to see risk distribution.")
        return
    
    # Create DataFrame for pie chart
    df = pd.DataFrame({
        "Risk Level": list(risk_dist.keys()),
        "Count": list(risk_dist.values())
    })
    
    # Display pie chart
    st.bar_chart(df.set_index("Risk Level"))
    
    # Display counts
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"✅ Safe: {risk_dist.get('Safe', 0)}")
    with col2:
        st.warning(f"⚠️ Suspicious: {risk_dist.get('Suspicious', 0)}")
    with col3:
        st.error(f"🚨 High Risk: {risk_dist.get('High Risk', 0)}")


def display_category_distribution(analytics: dict):
    """
    Display fraud category distribution as a bar chart.
    
    Args:
        analytics: Analytics data dictionary
    """
    st.markdown("### 🏷️ Fraud Category Distribution")
    
    category_dist = analytics.get("category_distribution", {})
    
    if not category_dist or sum(category_dist.values()) == 0:
        st.info("No data available yet. Analyze some messages to see category distribution.")
        return
    
    # Create DataFrame for bar chart
    df = pd.DataFrame({
        "Category": list(category_dist.keys()),
        "Count": list(category_dist.values())
    })
    
    # Sort by count descending
    df = df.sort_values("Count", ascending=False)
    
    # Display bar chart
    st.bar_chart(df.set_index("Category"))


def display_risk_trend(analytics: dict):
    """
    Display risk score trend over time as a line chart.
    
    Args:
        analytics: Analytics data dictionary
    """
    st.markdown("### 📈 Risk Score Trend Over Time")
    
    risk_trend = analytics.get("risk_trend", [])
    
    if not risk_trend:
        st.info("No data available yet. Analyze some messages to see trends.")
        return
    
    # Create DataFrame for line chart
    df = pd.DataFrame(risk_trend)
    
    if "timestamp" in df.columns and "risk_score" in df.columns:
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")
        
        # Display line chart
        st.line_chart(df["risk_score"])
    else:
        st.warning("Trend data format is invalid.")


def display_top_keywords(analytics: dict):
    """
    Display top 10 keywords as a bar chart.
    
    Args:
        analytics: Analytics data dictionary
    """
    st.markdown("### 🔑 Top 10 Scam Keywords")
    
    top_keywords = analytics.get("top_keywords", [])
    
    if not top_keywords:
        st.info("No keywords detected yet. Analyze some messages to see common patterns.")
        return
    
    # Create DataFrame for bar chart (limit to top 10)
    keywords_data = top_keywords[:10]
    df = pd.DataFrame(keywords_data, columns=["Keyword", "Count"])
    
    # Display bar chart
    st.bar_chart(df.set_index("Keyword"))


def display_history_controls():
    """Display history management controls."""
    st.markdown("### 🗑️ History Management")
    
    st.warning(
        "⚠️ **Warning:** Clearing history will permanently delete all analysis records. "
        "This action cannot be undone."
    )
    
    # Confirmation checkbox
    confirm = st.checkbox("I understand that this action is irreversible")
    
    # Clear button
    if st.button(
        "🗑️ Clear All History",
        type="secondary",
        disabled=not confirm,
        use_container_width=True
    ):
        if confirm:
            with st.spinner("Clearing history..."):
                success = clear_history()
            
            if success:
                st.success("✅ History cleared successfully!")
                st.balloons()
                # Clear session state
                if "awareness_score" in st.session_state:
                    del st.session_state["awareness_score"]
                if "awareness_level" in st.session_state:
                    del st.session_state["awareness_level"]
                # Rerun to refresh data
                st.rerun()


def display_sidebar():
    """Display sidebar with navigation and controls."""
    with st.sidebar:
        st.header("📊 Dashboard Controls")
        
        # Auto-refresh option
        auto_refresh = st.checkbox("Auto-refresh dashboard", value=False)
        
        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh interval (seconds)",
                min_value=5,
                max_value=60,
                value=10,
                step=5
            )
            st.info(f"Dashboard will refresh every {refresh_interval} seconds")
            # Trigger auto-refresh using st.rerun with time delay
            import time
            time.sleep(refresh_interval)
            st.rerun()
        
        # Manual refresh button
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        st.markdown("[← Back to Analysis](../)")
        
        st.markdown("---")
        
        # Privacy notice
        st.markdown("### 🔒 Privacy")
        st.caption(
            "All data is stored locally on your device. "
            "You can clear your history at any time using the controls below."
        )


def main():
    """Main dashboard function."""
    # Display header
    display_header()
    
    # Display sidebar
    display_sidebar()
    
    # Fetch analytics data
    with st.spinner("📊 Loading analytics..."):
        analytics = fetch_analytics()
    
    if not analytics:
        st.warning("Unable to load analytics data. Please check your connection and try again.")
        return
    
    # Check if there's any data
    total_messages = analytics.get("total_messages", 0)
    
    if total_messages == 0:
        st.info(
            "📭 **No data available yet**  \n"
            "Start analyzing messages to see your analytics dashboard populate with insights!"
        )
        st.markdown("[← Go to Analysis Page](../)")
        return
    
    # Display key metrics
    display_key_metrics(analytics)
    
    st.divider()
    
    # Display charts in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        display_risk_distribution(analytics)
        st.markdown("---")
        display_top_keywords(analytics)
    
    with col2:
        display_category_distribution(analytics)
        st.markdown("---")
        display_risk_trend(analytics)
    
    st.divider()
    
    # History management section
    display_history_controls()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <p>📊 Analytics Dashboard - Fraud Detection Platform</p>
            <p>Track your progress and stay informed about fraud patterns.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
