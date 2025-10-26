"""
SQL Analytics Page - REAL DATA ONLY
Uses actual players_real table from Cricbuzz database
NO MOCK DATA - Direct database connection
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import csv
import io
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cricbuzz.db')

def get_connection():
    """Get database connection"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None):
    """Execute a SQL query and return results"""
    conn = get_connection()
    if not conn:
        return None

    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return None
    finally:
        conn.close()

def export_to_csv(df, filename="query_results.csv"):
    """Export DataFrame to CSV"""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

# SQL QUERIES USING REAL DATA
SQL_QUERIES = {
    # BEGINNER LEVEL - Simple SELECT queries
    "Q1": {
        "title": "Q1: List All Indian Players",
        "description": "Retrieve all players from India",
        "difficulty": "Beginner",
        "sql": """
SELECT player_name, role, batting_style, bowling_style, international_team
FROM players_real
WHERE LOWER(international_team) LIKE '%india%'
ORDER BY player_name;
""",
        "concepts": ["SELECT", "FROM", "WHERE", "LIKE", "ORDER BY"]
    },

    "Q2": {
        "title": "Q2: Count Players by Team",
        "description": "Count how many players each international team has",
        "difficulty": "Beginner",
        "sql": """
SELECT international_team, COUNT(*) as player_count
FROM players_real
WHERE international_team IS NOT NULL AND international_team != ''
GROUP BY international_team
ORDER BY player_count DESC;
""",
        "concepts": ["COUNT", "GROUP BY", "ORDER BY DESC"]
    },

    "Q3": {
        "title": "Q3: List All Batsmen",
        "description": "Find all players who are batsmen",
        "difficulty": "Beginner",
        "sql": """
SELECT player_name, batting_style, international_team, team_name
FROM players_real
WHERE role LIKE '%Batsman%'
ORDER BY international_team, player_name;
""",
        "concepts": ["WHERE with LIKE", "Multiple column SELECT"]
    },

    "Q4": {
        "title": "Q4: Players with Detailed Stats",
        "description": "List players who have complete profile information",
        "difficulty": "Beginner",
        "sql": """
SELECT player_name, international_team, birth_place, date_of_birth
FROM players_real
WHERE has_detailed_stats = 1
ORDER BY international_team, player_name
LIMIT 20;
""",
        "concepts": ["WHERE with boolean", "LIMIT"]
    },

    "Q5": {
        "title": "Q5: Count Players by Role",
        "description": "Group players by their role and count them",
        "difficulty": "Beginner",
        "sql": """
SELECT role, COUNT(*) as player_count
FROM players_real
WHERE role IS NOT NULL AND role != ''
GROUP BY role
ORDER BY player_count DESC;
""",
        "concepts": ["GROUP BY", "COUNT", "ORDER BY"]
    },

    "Q6": {
        "title": "Q6: Right-Handed Batsmen",
        "description": "Find all right-handed batsmen",
        "difficulty": "Beginner",
        "sql": """
SELECT player_name, batting_style, international_team
FROM players_real
WHERE batting_style LIKE '%Right%'
ORDER BY international_team, player_name;
""",
        "concepts": ["WHERE with LIKE pattern matching"]
    },

    "Q7": {
        "title": "Q7: Players Born in Specific Cities",
        "description": "Find players born in Mumbai or Delhi",
        "difficulty": "Beginner",
        "sql": """
SELECT player_name, birth_place, date_of_birth, international_team
FROM players_real
WHERE LOWER(birth_place) LIKE '%mumbai%' 
   OR LOWER(birth_place) LIKE '%delhi%'
ORDER BY birth_place, player_name;
""",
        "concepts": ["OR operator", "Multiple LIKE conditions"]
    },

    "Q8": {
        "title": "Q8: Fast Bowlers",
        "description": "List all fast bowlers",
        "difficulty": "Beginner",
        "sql": """
SELECT player_name, bowling_style, international_team, role
FROM players_real
WHERE bowling_style LIKE '%fast%' 
   OR bowling_style LIKE '%Fast%'
ORDER BY international_team, player_name;
""",
        "concepts": ["WHERE with OR", "LIKE operator"]
    },

    # INTERMEDIATE LEVEL
    "Q9": {
        "title": "Q9: Players with Complete Profiles",
        "description": "Find players who have biography and detailed info",
        "difficulty": "Intermediate",
        "sql": """
SELECT player_name, international_team, birth_place, 
       CASE 
           WHEN LENGTH(bio) > 100 THEN 'Has Bio'
           ELSE 'No Bio'
       END as bio_status
FROM players_real
WHERE has_detailed_stats = 1
  AND bio IS NOT NULL
  AND LENGTH(bio) > 100
ORDER BY international_team, player_name
LIMIT 30;
""",
        "concepts": ["CASE WHEN", "LENGTH function", "Multiple conditions"]
    },

    "Q10": {
        "title": "Q10: All-Rounders by Team",
        "description": "Count all-rounders for each international team",
        "difficulty": "Intermediate",
        "sql": """
SELECT international_team, COUNT(*) as allrounder_count
FROM players_real
WHERE role LIKE '%All-rounder%' OR role LIKE '%all%rounder%'
GROUP BY international_team
HAVING allrounder_count > 0
ORDER BY allrounder_count DESC;
""",
        "concepts": ["HAVING clause", "Pattern matching with LIKE"]
    },

    "Q11": {
        "title": "Q11: Player Name Search",
        "description": "Search for players with 'Kumar' in their name",
        "difficulty": "Intermediate",
        "sql": """
SELECT player_name, international_team, role, batting_style
FROM players_real
WHERE player_name LIKE '%Kumar%'
ORDER BY player_name;
""",
        "concepts": ["String pattern matching", "LIKE with wildcards"]
    },

    "Q12": {
        "title": "Q12: Spin Bowlers Analysis",
        "description": "Find all spin bowlers grouped by bowling style",
        "difficulty": "Intermediate",
        "sql": """
SELECT bowling_style, international_team, COUNT(*) as spinner_count
FROM players_real
WHERE bowling_style LIKE '%spin%' 
   OR bowling_style LIKE '%Spin%'
GROUP BY bowling_style, international_team
HAVING spinner_count > 0
ORDER BY bowling_style, spinner_count DESC;
""",
        "concepts": ["GROUP BY multiple columns", "HAVING"]
    },

    "Q13": {
        "title": "Q13: Team Composition Analysis",
        "description": "Analyze team composition by role",
        "difficulty": "Intermediate",
        "sql": """
SELECT international_team, role, COUNT(*) as count
FROM players_real
WHERE international_team IN ('India', 'Australia', 'England', 'Pakistan')
  AND role IS NOT NULL
GROUP BY international_team, role
ORDER BY international_team, count DESC;
""",
        "concepts": ["IN operator", "GROUP BY multiple columns"]
    },

    "Q14": {
        "title": "Q14: Players by Birth Year",
        "description": "Group players by birth year (if available)",
        "difficulty": "Intermediate",
        "sql": """
SELECT 
    SUBSTR(date_of_birth, 1, 4) as birth_year,
    COUNT(*) as player_count
FROM players_real
WHERE date_of_birth IS NOT NULL 
  AND date_of_birth != ''
  AND LENGTH(date_of_birth) >= 4
GROUP BY birth_year
HAVING player_count > 5
ORDER BY birth_year DESC;
""",
        "concepts": ["SUBSTR function", "Date manipulation", "HAVING"]
    },

    "Q15": {
        "title": "Q15: Wicket Keepers",
        "description": "Find all wicket keepers across teams",
        "difficulty": "Intermediate",
        "sql": """
SELECT player_name, international_team, batting_style
FROM players_real
WHERE role LIKE '%Wicket%keeper%' 
   OR role LIKE '%wicket%keeper%'
   OR role LIKE '%WK%'
ORDER BY international_team, player_name;
""",
        "concepts": ["Multiple LIKE patterns", "Case-insensitive search"]
    },

    "Q16": {
        "title": "Q16: Player Distribution by Team",
        "description": "Show player distribution across top teams",
        "difficulty": "Intermediate",
        "sql": """
SELECT 
    international_team,
    COUNT(*) as total_players,
    SUM(CASE WHEN has_detailed_stats = 1 THEN 1 ELSE 0 END) as with_details,
    SUM(CASE WHEN has_detailed_stats = 0 THEN 1 ELSE 0 END) as without_details
FROM players_real
WHERE international_team IS NOT NULL
GROUP BY international_team
HAVING total_players >= 10
ORDER BY total_players DESC;
""",
        "concepts": ["SUM with CASE", "Aggregation", "HAVING"]
    },

    # ADVANCED LEVEL
    "Q17": {
        "title": "Q17: Detailed Team Statistics",
        "description": "Comprehensive team-wise player statistics",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    international_team,
    COUNT(*) as total_players,
    COUNT(CASE WHEN role LIKE '%Batsman%' THEN 1 END) as batsmen,
    COUNT(CASE WHEN role LIKE '%Bowler%' THEN 1 END) as bowlers,
    COUNT(CASE WHEN role LIKE '%All-rounder%' THEN 1 END) as allrounders,
    COUNT(CASE WHEN role LIKE '%Wicket%' THEN 1 END) as wicketkeepers,
    ROUND(100.0 * SUM(CASE WHEN has_detailed_stats = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as detail_percentage
FROM players_real
WHERE international_team IS NOT NULL AND international_team != ''
GROUP BY international_team
HAVING total_players >= 5
ORDER BY total_players DESC, detail_percentage DESC;
""",
        "concepts": ["Multiple COUNT with CASE", "Percentage calculation", "ROUND"]
    },

    "Q18": {
        "title": "Q18: Batting Styles Distribution",
        "description": "Analyze batting style distribution globally",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    batting_style,
    COUNT(*) as player_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM players_real WHERE batting_style IS NOT NULL), 2) as percentage,
    GROUP_CONCAT(DISTINCT international_team, ', ') as teams
FROM players_real
WHERE batting_style IS NOT NULL AND batting_style != ''
GROUP BY batting_style
ORDER BY player_count DESC;
""",
        "concepts": ["Subquery", "Percentage calculation", "GROUP_CONCAT"]
    },

    "Q19": {
        "title": "Q19: Player Completeness Score",
        "description": "Score players based on profile completeness",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    player_name,
    international_team,
    (CASE WHEN date_of_birth IS NOT NULL AND date_of_birth != '' THEN 1 ELSE 0 END +
     CASE WHEN birth_place IS NOT NULL AND birth_place != '' THEN 1 ELSE 0 END +
     CASE WHEN bio IS NOT NULL AND LENGTH(bio) > 50 THEN 1 ELSE 0 END +
     CASE WHEN teams_played IS NOT NULL AND teams_played != '' THEN 1 ELSE 0 END +
     CASE WHEN has_detailed_stats = 1 THEN 1 ELSE 0 END) as completeness_score
FROM players_real
WHERE international_team IS NOT NULL
ORDER BY completeness_score DESC, player_name
LIMIT 50;
""",
        "concepts": ["Complex CASE expressions", "Score calculation"]
    },

    "Q20": {
        "title": "Q20: Cross-Team Player Analysis",
        "description": "Find players who played for multiple teams",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    player_name,
    international_team,
    teams_played,
    LENGTH(teams_played) - LENGTH(REPLACE(teams_played, ',', '')) + 1 as team_count
FROM players_real
WHERE teams_played IS NOT NULL 
  AND teams_played LIKE '%,%'
ORDER BY team_count DESC, player_name
LIMIT 30;
""",
        "concepts": ["String functions", "REPLACE", "LENGTH"]
    },

    "Q21": {
        "title": "Q21: Bowling Style Diversity",
        "description": "Teams with most diverse bowling options",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    international_team,
    COUNT(DISTINCT bowling_style) as unique_bowling_styles,
    GROUP_CONCAT(DISTINCT bowling_style, ' | ') as bowling_types,
    COUNT(*) as total_bowlers
FROM players_real
WHERE bowling_style IS NOT NULL 
  AND bowling_style != ''
  AND bowling_style != 'N/A'
GROUP BY international_team
HAVING unique_bowling_styles >= 3
ORDER BY unique_bowling_styles DESC, total_bowlers DESC;
""",
        "concepts": ["COUNT DISTINCT", "GROUP_CONCAT with delimiter"]
    },

    "Q22": {
        "title": "Q22: Player Name Analysis",
        "description": "Analyze common first names in cricket",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    SUBSTR(player_name, 1, INSTR(player_name || ' ', ' ') - 1) as first_name,
    COUNT(*) as name_count,
    GROUP_CONCAT(international_team, ', ') as teams
FROM players_real
WHERE player_name IS NOT NULL AND player_name LIKE '% %'
GROUP BY first_name
HAVING name_count >= 3
ORDER BY name_count DESC, first_name
LIMIT 20;
""",
        "concepts": ["INSTR", "SUBSTR", "String extraction"]
    },

    "Q23": {
        "title": "Q23: Team Depth Analysis",
        "description": "Analyze team depth by role coverage",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    international_team,
    COUNT(*) as squad_size,
    COUNT(CASE WHEN role LIKE '%Batsman%' THEN 1 END) * 100.0 / COUNT(*) as batsman_percent,
    COUNT(CASE WHEN role LIKE '%Bowler%' THEN 1 END) * 100.0 / COUNT(*) as bowler_percent,
    COUNT(CASE WHEN role LIKE '%All-rounder%' THEN 1 END) * 100.0 / COUNT(*) as allrounder_percent,
    CASE 
        WHEN COUNT(CASE WHEN role LIKE '%Batsman%' THEN 1 END) >= 5 
         AND COUNT(CASE WHEN role LIKE '%Bowler%' THEN 1 END) >= 5 THEN 'Balanced'
        ELSE 'Unbalanced'
    END as squad_balance
FROM players_real
WHERE international_team IS NOT NULL AND role IS NOT NULL
GROUP BY international_team
HAVING squad_size >= 10
ORDER BY squad_size DESC;
""",
        "concepts": ["Percentage calculations", "Complex CASE", "Multiple aggregations"]
    },

    "Q24": {
        "title": "Q24: Player Information Quality",
        "description": "Evaluate data quality across teams",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    international_team,
    COUNT(*) as total_players,
    ROUND(AVG(CASE WHEN has_detailed_stats = 1 THEN 100 ELSE 0 END), 2) as avg_detail_score,
    SUM(CASE WHEN bio IS NOT NULL AND LENGTH(bio) > 200 THEN 1 ELSE 0 END) as players_with_bio,
    SUM(CASE WHEN date_of_birth IS NOT NULL AND date_of_birth != '' THEN 1 ELSE 0 END) as players_with_dob
FROM players_real
WHERE international_team IS NOT NULL
GROUP BY international_team
HAVING total_players >= 5
ORDER BY avg_detail_score DESC, total_players DESC;
""",
        "concepts": ["AVG with CASE", "Data quality metrics"]
    },

    "Q25": {
        "title": "Q25: Comprehensive Player Search",
        "description": "Advanced player search with multiple criteria",
        "difficulty": "Advanced",
        "sql": """
SELECT 
    player_name,
    international_team,
    role,
    batting_style,
    bowling_style,
    birth_place,
    CASE 
        WHEN has_detailed_stats = 1 THEN 'Complete Profile'
        ELSE 'Basic Info Only'
    END as profile_status,
    LENGTH(bio) as bio_length
FROM players_real
WHERE international_team IN ('India', 'Australia', 'England')
  AND role IS NOT NULL
  AND (batting_style LIKE '%Right%' OR bowling_style LIKE '%spin%')
ORDER BY international_team, player_name
LIMIT 50;
""",
        "concepts": ["IN operator", "Complex WHERE", "CASE expressions"]
    }
}

def show():
    """Main function to display SQL Analytics page"""
    st.markdown("### 📊 SQL Analytics - Interactive Cricket Data Analysis")
    st.info("**Using REAL DATA from Cricbuzz Database** - 800+ actual players, NO MOCK DATA")

    # Check if database exists
    if not os.path.exists(DB_PATH):
        st.error("❌ Database not found. Please run initialize_data.py first.")
        st.stop()

    # Show database info
    display_database_info()

    st.markdown("---")

    # Query selector
    display_query_selector()

def display_database_info():
    """Display information about the database"""
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()

            # Get player count
            cursor.execute("SELECT COUNT(*) FROM players_real")
            total_players = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM players_real WHERE has_detailed_stats = 1")
            detailed_players = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT international_team) FROM players_real WHERE international_team IS NOT NULL")
            total_teams = cursor.fetchone()[0]

            conn.close()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Players", total_players)
            with col2:
                st.metric("✅ With Details", detailed_players)
            with col3:
                st.metric("🌍 Teams", total_teams)

    except Exception as e:
        st.error(f"Error reading database: {e}")

def display_query_selector():
    """Display query selection and execution interface"""
    st.markdown("### 🔍 Select a SQL Query")

    # Filter by difficulty
    difficulty_filter = st.selectbox(
        "Filter by Difficulty",
        ["All", "Beginner", "Intermediate", "Advanced"]
    )

    # Get filtered queries
    filtered_queries = {}
    for key, query in SQL_QUERIES.items():
        if difficulty_filter == "All" or query["difficulty"] == difficulty_filter:
            filtered_queries[key] = query

    st.info(f"📝 Showing {len(filtered_queries)} queries")

    # Query selection
    query_options = {f"{key}: {query['title']}" : key for key, query in filtered_queries.items()}

    selected_display = st.selectbox(
        "Choose a Query",
        options=list(query_options.keys())
    )

    selected_key = query_options[selected_display]
    selected_query = SQL_QUERIES[selected_key]

    # Display query details
    display_query_details(selected_key, selected_query)

def display_query_details(query_key, query_info):
    """Display and execute selected query"""
    st.markdown("---")
    st.markdown(f"### {query_info['title']}")
    st.markdown(f"**Difficulty:** `{query_info['difficulty']}`")
    st.markdown(f"**Description:** {query_info['description']}")

    # Show SQL concepts
    st.markdown("**📚 SQL Concepts:**")
    st.markdown(" • " + " • ".join(query_info['concepts']))

    # Show SQL query
    with st.expander("📝 View SQL Query", expanded=True):
        st.code(query_info['sql'], language='sql')

    # Execute query button
    if st.button("▶️ Execute Query", key=f"exec_{query_key}"):
        with st.spinner("Executing query..."):
            df = execute_query(query_info['sql'])

            if df is not None and not df.empty:
                st.success(f"✅ Query executed successfully! Found {len(df)} records")

                # Display results
                st.dataframe(df, use_container_width=True)

                # Export option
                csv_data = export_to_csv(df)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"{query_key}_results.csv",
                    mime="text/csv"
                )

                # Show query stats
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows Returned", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))

            elif df is not None:
                st.warning("Query executed but returned no results")
            else:
                st.error("Query execution failed. Check the SQL syntax.")

if __name__ == "__main__":
    show()
