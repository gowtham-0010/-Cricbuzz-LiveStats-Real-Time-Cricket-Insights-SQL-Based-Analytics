"""
Home Page - Cricket Dashboard Overview
Provides project information and navigation guidance
"""

import streamlit as st

def show():
    """Display the home page content"""

    # Main title and description
    st.markdown("## Welcome to Cricbuzz LiveStats Dashboard! 🏏")

    st.markdown("""
    ### 🎯 About This Project

    **Cricbuzz LiveStats** is a comprehensive cricket analytics dashboard that integrates live data 
    from the Cricbuzz API with a SQL database to create an interactive web application. 

    This platform delivers:
    - ⚡ **Real-time match updates**
    - 📊 **Detailed player statistics** 
    - 🔍 **SQL-driven analytics**
    - 🛠️ **Full CRUD operations** for data management
    """)

    # Features overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🌟 Key Features

        #### 🏏 Live Scores
        - View ongoing matches from Cricbuzz API
        - Real-time scorecards and match status
        - Detailed venue and team information
        - Live commentary and match events

        #### 📊 Player Stats  
        - Search players by name
        - View comprehensive player profiles
        - Batting and bowling career statistics
        - Performance across different formats
        """)

    with col2:
        st.markdown("""
        ### 🔧 Advanced Tools

        #### 🔍 SQL Analytics
        - 25+ pre-built SQL queries 
        - Beginner to advanced difficulty levels
        - Interactive query execution
        - Export results as CSV

        #### ⚙️ CRUD Operations
        - Create new player records
        - View all players in database
        - Update existing player information  
        - Delete player records safely
        """)

    # Technology stack
    st.markdown("### 🛠️ Technology Stack")

    tech_col1, tech_col2, tech_col3 = st.columns(3)

    with tech_col1:
        st.markdown("""
        **Frontend**
        - Streamlit
        - HTML/CSS
        - Modern UI Components
        """)

    with tech_col2:
        st.markdown("""
        **Backend**  
        - Python
        - SQLite Database
        - Pandas for data processing
        """)

    with tech_col3:
        st.markdown("""
        **APIs & External**
        - Cricbuzz API via RapidAPI
        - REST API Integration
        - JSON data processing
        """)

    # Business use cases
    st.markdown("### 💼 Business Use Cases")

    use_cases = [
        {
            "icon": "📺",
            "title": "Sports Media & Broadcasting",
            "description": "Real-time match updates for commentary teams and player performance analysis"
        },
        {
            "icon": "🎮", 
            "title": "Fantasy Cricket Platforms",
            "description": "Player form analysis, head-to-head statistics, and real-time score updates"
        },
        {
            "icon": "📈",
            "title": "Cricket Analytics Firms", 
            "description": "Advanced statistical modeling, performance trends, and data-driven insights"
        },
        {
            "icon": "🎓",
            "title": "Educational Institutions",
            "description": "Teaching database operations with real-world data and SQL practice"
        }
    ]

    for i, use_case in enumerate(use_cases):
        if i % 2 == 0:
            col1, col2 = st.columns(2)
            current_col = col1
        else:
            current_col = col2

        with current_col:
            st.markdown(f"""
            **{use_case['icon']} {use_case['title']}**

            {use_case['description']}
            """)

    # Navigation guide
    st.markdown("### 🧭 Navigation Guide")

    nav_info = """
    **Getting Started:**

    1. **🏏 Live Scores** - Start here to explore real-time cricket matches
    2. **📊 Player Stats** - Search and analyze individual player performance  
    3. **🔍 SQL Analytics** - Practice SQL with 25+ cricket-themed queries
    4. **⚙️ CRUD Operations** - Manage player database records

    **Connection Status** (shown in sidebar):
    - ✅ Green: System is working properly
    - ❌ Red: Connection issues detected
    """

    st.info(nav_info)

    # Quick start section
    st.markdown("### 🚀 Quick Start")

    quick_start_col1, quick_start_col2 = st.columns(2)

    with quick_start_col1:
        st.markdown("""
        **For Cricket Fans:**
        1. Go to "Live Scores" to see current matches
        2. Select any match to view detailed scorecards
        3. Explore player statistics in "Player Stats"
        """)

    with quick_start_col2:
        st.markdown("""
        **For SQL Learners:**
        1. Visit "SQL Analytics" page
        2. Choose from 25 practice queries
        3. Execute queries and download results
        4. Try "CRUD Operations" for hands-on practice
        """)

    # Footer information
    st.markdown("---")
    st.markdown("""
    ### 📋 Project Information

    - **Skills:** Python • SQL • Streamlit • JSON • REST API
    - **Domain:** Sports Analytics
    - **Database:** SQLite with optimized cricket schema
    - **API Rate Limit:** Respectful usage with 300ms delays between requests

    **Note:** This dashboard uses real Cricbuzz data via RapidAPI. 
    Live features depend on API availability and cricket match schedules.
    """)
