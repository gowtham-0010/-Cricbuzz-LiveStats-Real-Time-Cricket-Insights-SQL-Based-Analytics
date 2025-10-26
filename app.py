"""
🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics
Main Streamlit Application Entry Point - Complete Implementation
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import page modules
from pages import home, live_matches, top_stats, sql_queries, crud_operations
from utils.db_connection import init_database, check_db_connection
from utils.api_utils import check_api_connection

# Configure Streamlit page
st.set_page_config(
    page_title="🏏 Cricbuzz Live Match Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI with FIXED DROPDOWN STYLING
st.markdown("""
<style>
    /* Main Dashboard Title */
    .main-dashboard-title {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-dashboard-title h1 {
        color: white;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 1px;
    }

    /* Sidebar Styling */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
    }

    .connection-status {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }

    .status-connected {
        color: #28a745;
        font-weight: bold;
        font-size: 0.9rem;
    }

    .status-disconnected {
        color: #dc3545;
        font-weight: bold;
        font-size: 0.9rem;
    }

    /* FIXED DROPDOWN STYLING - Making text visible */
    .stSelectbox label {
        font-weight: 600 !important;
        color: #2d3436 !important;
        font-size: 1rem !important;
    }

    /* Dropdown container */
    .stSelectbox > div > div {
        background-color: white !important;
        border-radius: 8px !important;
        border: 2px solid #e9ecef !important;
    }

    /* Selected value in dropdown */
    .stSelectbox > div > div > div {
        color: #2d3436 !important;
        font-weight: 500 !important;
    }

    /* Dropdown options when opened */
    .stSelectbox div[data-baseweb="select"] div {
        color: #2d3436 !important;
        background-color: white !important;
    }

    /* Dropdown menu items */
    .stSelectbox div[role="listbox"] div {
        color: #2d3436 !important;
        background-color: white !important;
    }

    /* Hover effect on dropdown items */
    .stSelectbox div[role="listbox"] div:hover {
        background-color: #f8f9fa !important;
        color: #495057 !important;
    }

    /* Match Selection Dropdown */
    .match-selector {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    /* Match Details Cards */
    .match-details-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .match-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3436;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Score Display */
    .current-score {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }

    /* Scorecard Button */
    .scorecard-button {
        background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: transform 0.2s;
    }

    .scorecard-button:hover {
        transform: translateY(-2px);
    }

    /* Data Tables */
    .scorecard-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    /* Player Search */
    .player-search-container {
        background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
    }

    /* Tabs Styling */
    .player-tabs {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* SQL Query Editor */
    .sql-editor-container {
        background: #2d3436;
        color: #ddd;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
    }

    /* CRUD Forms */
    .crud-form-container {
        background: linear-gradient(135deg, #fab1a0 0%, #e17055 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
    }

    /* Warning Messages */
    .warning-message {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #f39c12;
    }

    /* Success Messages */
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }

    /* Button Styles */
    .action-button {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        margin: 0.3rem;
        transition: all 0.3s ease;
    }

    .action-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .danger-button {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        margin: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application logic with sidebar dropdown navigation"""

    # Initialize database
    init_database()

    # Sidebar Navigation - Left Side Component
    with st.sidebar:
        # Cricket Dashboard Title
        st.markdown("""
        <div class="sidebar-header">
            🏏 Cricket Dashboard
        </div>
        """, unsafe_allow_html=True)

        # Choose a Page Dropdown
        st.markdown("**Choose a page:**")

        page_options = {
            "1. Live Scores": "live_scores",
            "2. Player Stats": "player_stats", 
            "3. SQL Analytics": "sql_analytics",
            "4. CRUD Operations": "crud_operations"
        }

        selected_page = st.selectbox(
            "Select option:",
            options=list(page_options.keys()),
            index=0,
            key="page_selector",
            help="Choose the section you want to explore"
        )

        st.markdown("---")

        # Connection Status Section
        st.markdown("### Connection Status")

        # Database Status
        db_status = check_db_connection()
        if db_status:
            st.markdown("""
            <div class="connection-status">
                <span class="status-connected">✅ Database Connected</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="connection-status" style="border-left-color: #dc3545;">
                <span class="status-disconnected">❌ Database Error</span>
            </div>
            """, unsafe_allow_html=True)

        # API Status
        api_status = check_api_connection()
        if api_status:
            st.markdown("""
            <div class="connection-status">
                <span class="status-connected">✅ API Connected</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="connection-status" style="border-left-color: #dc3545;">
                <span class="status-disconnected">❌ API Error</span>
            </div>
            """, unsafe_allow_html=True)

    # Main Page Section - Dynamic Components
    page_value = page_options[selected_page]

    # Display main dashboard title - BOLD SIZE TITLE
    st.markdown("""
    <div class="main-dashboard-title">
        <h1>CRICBUZZ LIVE MATCH DASHBOARD</h1>
    </div>
    """, unsafe_allow_html=True)

    # Route to appropriate page based on selection
    if page_value == "live_scores":
        live_matches.show()
    elif page_value == "player_stats":
        top_stats.show()
    elif page_value == "sql_analytics":
        sql_queries.show()
    elif page_value == "crud_operations":
        crud_operations.show()

if __name__ == "__main__":
    main()
