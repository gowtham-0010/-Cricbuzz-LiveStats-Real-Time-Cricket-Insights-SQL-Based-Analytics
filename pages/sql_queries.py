"""
SQL Analytics Page - Interactive Cricket Data Analytics
Execute 25+ SQL queries with progressive difficulty levels
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
        st.error(f"Database error: {str(e)}")
        return None
    finally:
        conn.close()

def init_sample_database():
    """Initialize database with sample tables and data"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Create teams table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY,
                team_name TEXT UNIQUE NOT NULL,
                team_sname TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create venues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                venue_id INTEGER PRIMARY KEY,
                venue_name TEXT NOT NULL,
                city TEXT,
                country TEXT,
                capacity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create series table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                series_id INTEGER PRIMARY KEY,
                series_name TEXT NOT NULL,
                host_country TEXT,
                start_date DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY,
                match_desc TEXT,
                match_format TEXT,
                match_date DATE,
                series_id INTEGER,
                team1_id INTEGER,
                team2_id INTEGER,
                venue_id INTEGER,
                toss_winner_id INTEGER,
                toss_decision TEXT,
                match_winner_id INTEGER,
                victory_margin INTEGER,
                victory_type TEXT,
                match_status TEXT DEFAULT 'Completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (series_id) REFERENCES series (series_id),
                FOREIGN KEY (team1_id) REFERENCES teams (team_id),
                FOREIGN KEY (team2_id) REFERENCES teams (team_id),
                FOREIGN KEY (venue_id) REFERENCES venues (venue_id),
                FOREIGN KEY (toss_winner_id) REFERENCES teams (team_id),
                FOREIGN KEY (match_winner_id) REFERENCES teams (team_id)
            )
        """)

        # Create players table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY,
                player_name TEXT NOT NULL,
                team_id INTEGER,
                role TEXT,
                batting_style TEXT,
                bowling_style TEXT,
                nationality TEXT,
                date_of_birth DATE,
                matches_played INTEGER DEFAULT 0,
                runs_scored INTEGER DEFAULT 0,
                wickets_taken INTEGER DEFAULT 0,
                batting_average REAL DEFAULT 0.0,
                bowling_average REAL DEFAULT 0.0,
                strike_rate REAL DEFAULT 0.0,
                economy_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        """)

        # Create player_match_performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_match_performance (
                performance_id INTEGER PRIMARY KEY,
                player_id INTEGER,
                match_id INTEGER,
                team_id INTEGER,
                innings_number INTEGER,
                batting_order INTEGER,
                runs_scored INTEGER DEFAULT 0,
                balls_faced INTEGER DEFAULT 0,
                strike_rate REAL DEFAULT 0.0,
                overs_bowled REAL DEFAULT 0.0,
                wickets_taken INTEGER DEFAULT 0,
                runs_conceded INTEGER DEFAULT 0,
                economy_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (player_id),
                FOREIGN KEY (match_id) REFERENCES matches (match_id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        """)

        # Insert sample data
        insert_comprehensive_sample_data(cursor)

        conn.commit()
        logger.info("Sample database initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def insert_comprehensive_sample_data(cursor):
    """Insert comprehensive sample data for all tables"""
    try:
        # Sample teams
        teams_data = [
            (1, 'India', 'IND', 'India'),
            (2, 'Australia', 'AUS', 'Australia'), 
            (3, 'England', 'ENG', 'England'),
            (4, 'Pakistan', 'PAK', 'Pakistan'),
            (5, 'South Africa', 'SA', 'South Africa'),
            (6, 'New Zealand', 'NZ', 'New Zealand')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO teams (team_id, team_name, team_sname, country) 
            VALUES (?, ?, ?, ?)
        """, teams_data)

        # Sample venues
        venues_data = [
            (1, 'Wankhede Stadium', 'Mumbai', 'India', 33108),
            (2, 'Melbourne Cricket Ground', 'Melbourne', 'Australia', 100024),
            (3, 'Lords Cricket Ground', 'London', 'England', 28000),
            (4, 'Eden Gardens', 'Kolkata', 'India', 66000)
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO venues (venue_id, venue_name, city, country, capacity) 
            VALUES (?, ?, ?, ?, ?)
        """, venues_data)

        # Sample series
        series_data = [
            (1, 'India vs Australia 2024', 'India', '2024-01-01', '2024-01-30'),
            (2, 'England vs Pakistan 2024', 'England', '2024-03-01', '2024-03-25'),
            (3, 'World Cup 2024', 'India', '2024-10-01', '2024-11-15')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO series (series_id, series_name, host_country, start_date, end_date) 
            VALUES (?, ?, ?, ?, ?)
        """, series_data)

        # Sample matches
        matches_data = [
            (1, 'India vs Australia 1st ODI', 'ODI', '2024-01-15', 1, 1, 2, 1, 1, 'bat', 1, 45, 'runs', 'Completed'),
            (2, 'India vs Australia 2nd ODI', 'ODI', '2024-01-18', 1, 1, 2, 2, 2, 'bowl', 2, 6, 'wickets', 'Completed'),
            (3, 'England vs Pakistan 1st Test', 'Test', '2024-03-05', 2, 3, 4, 3, 3, 'bat', 3, 8, 'wickets', 'Completed')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO matches (match_id, match_desc, match_format, match_date, series_id, 
                                         team1_id, team2_id, venue_id, toss_winner_id, toss_decision, 
                                         match_winner_id, victory_margin, victory_type, match_status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, matches_data)

        # Sample players
        players_data = [
            (1, 'Virat Kohli', 1, 'Batsman', 'Right-handed', 'Right-arm medium', 'Indian', '1988-11-05', 274, 12169, 4, 58.18, 77.0, 93.17, 7.2),
            (2, 'Rohit Sharma', 1, 'Batsman', 'Right-handed', 'Right-arm off-break', 'Indian', '1987-04-30', 243, 9205, 8, 46.86, 45.5, 88.9, 8.1),
            (3, 'Steve Smith', 2, 'Batsman', 'Right-handed', 'Right-arm leg-break', 'Australian', '1989-06-02', 138, 8010, 17, 61.8, 35.2, 86.4, 6.8),
            (4, 'Joe Root', 3, 'Batsman', 'Right-handed', 'Right-arm off-break', 'English', '1991-12-30', 151, 9300, 32, 49.2, 42.1, 84.7, 7.1),
            (5, 'Babar Azam', 4, 'Batsman', 'Right-handed', 'Right-arm medium', 'Pakistani', '1994-10-15', 102, 4442, 0, 45.5, 0.0, 87.2, 0.0),
            (6, 'Pat Cummins', 2, 'Bowler', 'Right-handed', 'Right-arm fast', 'Australian', '1993-05-08', 44, 535, 164, 19.4, 28.2, 79.1, 2.8),
            (7, 'Jasprit Bumrah', 1, 'Bowler', 'Right-handed', 'Right-arm fast', 'Indian', '1993-12-06', 30, 99, 128, 8.3, 20.2, 65.4, 4.1)
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO players 
            (player_id, player_name, team_id, role, batting_style, bowling_style, 
             nationality, date_of_birth, matches_played, runs_scored, wickets_taken, 
             batting_average, bowling_average, strike_rate, economy_rate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, players_data)

        # Sample player match performances
        performance_data = [
            (1, 1, 1, 1, 1, 3, 89, 95, 93.7, 0.0, 0, 0, 0.0),
            (2, 2, 1, 1, 1, 1, 142, 137, 103.6, 0.0, 0, 0, 0.0),
            (3, 3, 1, 2, 1, 4, 67, 78, 85.9, 0.0, 0, 0, 0.0),
            (4, 6, 2, 2, 2, 8, 25, 18, 138.9, 8.5, 3, 42, 4.9),
            (5, 7, 2, 1, 2, 11, 5, 8, 62.5, 9.0, 4, 38, 4.2)
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO player_match_performance 
            (performance_id, player_id, match_id, team_id, innings_number, batting_order,
             runs_scored, balls_faced, strike_rate, overs_bowled, wickets_taken, runs_conceded, economy_rate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, performance_data)

    except Exception as e:
        logger.error(f"Sample data insertion error: {e}")

def show():
    """Display the SQL analytics page"""
    st.markdown("## 🔍 SQL Analytics")
    st.markdown("Practice SQL with 25+ cricket-themed queries across three difficulty levels")

    # Initialize database on first run
    if st.button("🔄 Initialize Sample Database", help="Click to set up sample data for queries"):
        with st.spinner("Setting up sample database..."):
            if init_sample_database():
                st.success("✅ Sample database initialized successfully!")
                st.info("You can now execute SQL queries on the sample cricket data.")
            else:
                st.error("❌ Failed to initialize database. Check the logs for details.")

    # Query selector
    display_query_selector()

    # About SQL Analytics
    display_about_section()

def display_query_selector():
    """Display query selection and execution interface"""
    # Define all queries
    queries = get_all_queries()

    # Create query options for dropdown
    query_options = {}
    for i, query_data in enumerate(queries, 1):
        display_name = f"Q{i}: {query_data['title']} ({query_data['difficulty']})"
        query_options[display_name] = query_data

    # Query selection
    st.markdown("### Select a Query")
    selected_query_name = st.selectbox(
        "Choose from 25 SQL practice queries:",
        options=list(query_options.keys()),
        index=0,
        key="query_selector"
    )

    if selected_query_name:
        selected_query = query_options[selected_query_name]
        display_query_interface(selected_query)

def display_query_interface(query_data):
    """Display the query execution interface"""
    # Query information
    st.markdown(f"### {query_data['title']}")
    st.markdown(f"**Difficulty Level:** {get_difficulty_badge(query_data['difficulty'])}")
    st.markdown(f"**Description:** {query_data['description']}")

    # SQL query editor
    st.markdown("#### SQL Query")
    query_text = st.text_area(
        "SQL Command:",
        value=query_data['sql'],
        height=150,
        key=f"query_editor_{hash(query_data['title'])}"
    )

    # Execute button
    col1, col2 = st.columns([1, 4])
    with col1:
        execute_clicked = st.button("▶️ Execute Query", key="execute_query", type="primary")

    # Execute query and display results
    if execute_clicked:
        if query_text.strip():
            execute_and_display_query(query_text, query_data['title'])
        else:
            st.error("❌ Please enter a SQL query to execute")

def execute_and_display_query(query_text, query_title):
    """Execute SQL query and display results"""
    with st.spinner("Executing query..."):
        try:
            result_df = execute_query(query_text)

            if result_df is not None and not result_df.empty:
                st.success(f"✅ Query executed successfully! Found {len(result_df)} rows.")

                # Display results
                st.markdown("#### 📊 Query Results")
                st.dataframe(result_df, use_container_width=True)

                # Download button
                display_download_button(result_df, query_title)

                # Query statistics
                display_query_stats(result_df)

            elif result_df is not None and result_df.empty:
                st.warning("⚠️ Query executed successfully but returned no results.")
                st.info("This might be expected for certain queries or indicate that no data matches the criteria.")
            else:
                st.error("❌ Query execution failed. Please check your SQL syntax and database connection.")
                st.info("""
                **Troubleshooting Tips:**
                1. Click 'Initialize Sample Database' if you haven't done so
                2. Check SQL syntax (proper table and column names)
                3. Ensure database file has proper permissions
                4. Try a simpler query first to test connection
                """)

        except Exception as e:
            st.error(f"❌ Error executing query: {str(e)}")
            st.info("""
            **Common Issues:**
            - Check SQL syntax and spelling
            - Verify table and column names exist
            - Ensure proper JOIN conditions
            - Initialize sample database if not done
            """)

def display_download_button(df, query_title):
    """Display download button for query results"""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    filename = f"cricket_query_results_{query_title.replace(' ', '_').lower()}.csv"
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=f"download_{hash(query_title)}"
    )

def display_query_stats(df):
    """Display statistics about query results"""
    st.markdown("#### 📈 Result Statistics")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Total Rows", len(df))
    with stat_col2:
        st.metric("Total Columns", len(df.columns))
    with stat_col3:
        numeric_cols = df.select_dtypes(include=['number']).columns
        st.metric("Numeric Columns", len(numeric_cols))
    with stat_col4:
        text_cols = df.select_dtypes(include=['object']).columns
        st.metric("Text Columns", len(text_cols))

def get_difficulty_badge(difficulty):
    """Get colored badge for difficulty level"""
    badges = {
        "Beginner": "🟢 Beginner",
        "Intermediate": "🟡 Intermediate", 
        "Advanced": "🔴 Advanced"
    }
    return badges.get(difficulty, "⚪ Unknown")

def get_all_queries():
    """Return all 25 SQL queries with metadata"""
    return [
        # BEGINNER LEVEL (Questions 1-8)
        {
            "title": "Find all Indian players",
            "difficulty": "Beginner",
            "description": "Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
            "sql": """SELECT player_name, role, batting_style, bowling_style, nationality
FROM players 
WHERE LOWER(nationality) LIKE '%indian%'
ORDER BY player_name;"""
        },
        {
            "title": "Top 5 highest run scorers",
            "difficulty": "Beginner",
            "description": "List the top 5 highest run scorers. Show player name, total runs, batting average, and matches played.",
            "sql": """SELECT player_name, runs_scored, batting_average, matches_played
FROM players
WHERE matches_played > 10
ORDER BY runs_scored DESC
LIMIT 5;"""
        },
        {
            "title": "Large capacity venues",
            "difficulty": "Beginner",
            "description": "Display all cricket venues that have a seating capacity of more than 50,000 spectators.",
            "sql": """SELECT venue_name, city, country, capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;"""
        },
        {
            "title": "Team information",
            "difficulty": "Beginner",
            "description": "Show all team information including team name, short name, and country.",
            "sql": """SELECT team_name, team_sname, country
FROM teams
ORDER BY team_name;"""
        },
        {
            "title": "Players by role",
            "difficulty": "Beginner", 
            "description": "Count how many players belong to each playing role (Batsman, Bowler, All-rounder, Wicket-keeper).",
            "sql": """SELECT role, COUNT(*) as player_count
FROM players
WHERE role IS NOT NULL AND role != ''
GROUP BY role
ORDER BY player_count DESC;"""
        },
        {
            "title": "Recent matches",
            "difficulty": "Beginner",
            "description": "Show recent matches with match description, format, and date.",
            "sql": """SELECT match_desc, match_format, match_date, match_status
FROM matches
ORDER BY match_date DESC
LIMIT 10;"""
        },
        {
            "title": "Batsmen with high averages",
            "difficulty": "Beginner",
            "description": "Find batsmen with batting average above 45.",
            "sql": """SELECT player_name, batting_average, runs_scored, matches_played
FROM players
WHERE role = 'Batsman' AND batting_average > 45
ORDER BY batting_average DESC;"""
        },
        {
            "title": "Series in 2024",
            "difficulty": "Beginner",
            "description": "Show all cricket series that started in 2024.",
            "sql": """SELECT series_name, host_country, start_date, end_date
FROM series
WHERE strftime('%Y', start_date) = '2024'
ORDER BY start_date;"""
        },

        # INTERMEDIATE LEVEL (Questions 9-16)
        {
            "title": "Players with 1000+ runs and 10+ wickets",
            "difficulty": "Intermediate",
            "description": "Find players who have scored more than 1000 runs AND taken more than 10 wickets.",
            "sql": """SELECT p.player_name, p.runs_scored, p.wickets_taken, p.role
FROM players p
WHERE p.runs_scored >= 1000 AND p.wickets_taken >= 10
ORDER BY (p.runs_scored + p.wickets_taken * 20) DESC;"""
        },
        {
            "title": "Team match results",
            "difficulty": "Intermediate",
            "description": "Show match results with team names instead of IDs.",
            "sql": """SELECT m.match_desc, t1.team_name as team1, t2.team_name as team2,
       tw.team_name as winner, m.victory_margin, m.victory_type
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
LEFT JOIN teams tw ON m.match_winner_id = tw.team_id
ORDER BY m.match_date DESC;"""
        },
        {
            "title": "Player performance summary",
            "difficulty": "Intermediate",
            "description": "Show total runs and wickets by each player across all matches.",
            "sql": """SELECT p.player_name, 
       SUM(pmp.runs_scored) as total_match_runs,
       SUM(pmp.wickets_taken) as total_match_wickets,
       COUNT(pmp.match_id) as matches_played_detailed
FROM players p
JOIN player_match_performance pmp ON p.player_id = pmp.player_id
GROUP BY p.player_id, p.player_name
ORDER BY total_match_runs DESC;"""
        },
        {
            "title": "Venue match count",
            "difficulty": "Intermediate",
            "description": "Count how many matches were played at each venue.",
            "sql": """SELECT v.venue_name, v.city, v.country, COUNT(m.match_id) as matches_played
FROM venues v
LEFT JOIN matches m ON v.venue_id = m.venue_id
GROUP BY v.venue_id, v.venue_name, v.city, v.country
ORDER BY matches_played DESC;"""
        },
        {
            "title": "Best bowling performances",
            "difficulty": "Intermediate", 
            "description": "Find the best bowling performances (most wickets in a single match).",
            "sql": """SELECT p.player_name, pmp.wickets_taken, m.match_desc, pmp.economy_rate
FROM player_match_performance pmp
JOIN players p ON pmp.player_id = p.player_id
JOIN matches m ON pmp.match_id = m.match_id
WHERE pmp.wickets_taken > 0
ORDER BY pmp.wickets_taken DESC
LIMIT 10;"""
        },
        {
            "title": "High scoring innings",
            "difficulty": "Intermediate",
            "description": "Find innings where players scored 50 or more runs.",
            "sql": """SELECT p.player_name, pmp.runs_scored, pmp.balls_faced, pmp.strike_rate, m.match_desc
FROM player_match_performance pmp
JOIN players p ON pmp.player_id = p.player_id
JOIN matches m ON pmp.match_id = m.match_id
WHERE pmp.runs_scored >= 50
ORDER BY pmp.runs_scored DESC;"""
        },
        {
            "title": "Team performance in matches",
            "difficulty": "Intermediate",
            "description": "Count wins for each team.",
            "sql": """SELECT t.team_name, COUNT(m.match_id) as total_wins
FROM teams t
LEFT JOIN matches m ON t.team_id = m.match_winner_id
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;"""
        },
        {
            "title": "Player averages by team",
            "difficulty": "Intermediate",
            "description": "Show average batting and bowling statistics for each team.",
            "sql": """SELECT t.team_name,
       AVG(p.batting_average) as avg_batting_average,
       AVG(p.bowling_average) as avg_bowling_average,
       COUNT(p.player_id) as total_players
FROM teams t
JOIN players p ON t.team_id = p.team_id
GROUP BY t.team_id, t.team_name
ORDER BY avg_batting_average DESC;"""
        },

        # ADVANCED LEVEL (Questions 17-25)
        {
            "title": "Toss advantage analysis",
            "difficulty": "Advanced",
            "description": "Analyze whether winning the toss gives teams an advantage.",
            "sql": """SELECT m.toss_decision,
       COUNT(*) as total_matches,
       SUM(CASE WHEN m.toss_winner_id = m.match_winner_id THEN 1 ELSE 0 END) as toss_winner_also_match_winner,
       ROUND(100.0 * SUM(CASE WHEN m.toss_winner_id = m.match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 2) as win_percentage
FROM matches m
WHERE m.toss_winner_id IS NOT NULL AND m.match_winner_id IS NOT NULL
GROUP BY m.toss_decision
ORDER BY win_percentage DESC;"""
        },
        {
            "title": "Most consistent performers",
            "difficulty": "Advanced", 
            "description": "Find players with most consistent performance (low standard deviation in runs).",
            "sql": """SELECT p.player_name,
       AVG(pmp.runs_scored) as avg_runs_per_match,
       COUNT(pmp.match_id) as matches_analyzed,
       MIN(pmp.runs_scored) as min_score,
       MAX(pmp.runs_scored) as max_score
FROM players p
JOIN player_match_performance pmp ON p.player_id = pmp.player_id
GROUP BY p.player_id, p.player_name
HAVING COUNT(pmp.match_id) >= 2
ORDER BY avg_runs_per_match DESC;"""
        },
        {
            "title": "Match format comparison",
            "difficulty": "Advanced",
            "description": "Compare average scores across different match formats.",
            "sql": """SELECT m.match_format,
       AVG(pmp.runs_scored) as avg_runs_per_innings,
       AVG(pmp.strike_rate) as avg_strike_rate,
       COUNT(DISTINCT pmp.match_id) as total_matches
FROM matches m
JOIN player_match_performance pmp ON m.match_id = pmp.match_id
WHERE pmp.runs_scored > 0
GROUP BY m.match_format
ORDER BY avg_runs_per_innings DESC;"""
        },
        {
            "title": "Player impact analysis",
            "difficulty": "Advanced",
            "description": "Calculate player impact based on runs and wickets contribution.",
            "sql": """SELECT p.player_name,
       SUM(pmp.runs_scored) as total_runs,
       SUM(pmp.wickets_taken) as total_wickets,
       (SUM(pmp.runs_scored) + SUM(pmp.wickets_taken) * 25) as impact_score
FROM players p
JOIN player_match_performance pmp ON p.player_id = pmp.player_id
GROUP BY p.player_id, p.player_name
HAVING COUNT(pmp.match_id) >= 1
ORDER BY impact_score DESC
LIMIT 10;"""
        },
        {
            "title": "Venue advantage analysis",
            "difficulty": "Advanced",
            "description": "Analyze which teams perform better at specific venues.",
            "sql": """SELECT v.venue_name, t.team_name,
       COUNT(CASE WHEN m.match_winner_id = t.team_id THEN 1 END) as wins,
       COUNT(CASE WHEN m.team1_id = t.team_id OR m.team2_id = t.team_id THEN 1 END) as total_matches,
       ROUND(100.0 * COUNT(CASE WHEN m.match_winner_id = t.team_id THEN 1 END) / 
             NULLIF(COUNT(CASE WHEN m.team1_id = t.team_id OR m.team2_id = t.team_id THEN 1 END), 0), 2) as win_percentage
FROM venues v
JOIN matches m ON v.venue_id = m.venue_id
JOIN teams t ON (m.team1_id = t.team_id OR m.team2_id = t.team_id)
GROUP BY v.venue_id, v.venue_name, t.team_id, t.team_name
HAVING total_matches >= 1
ORDER BY v.venue_name, win_percentage DESC;"""
        },
        {
            "title": "Performance trends",
            "difficulty": "Advanced",
            "description": "Analyze performance trends over time for top players.",
            "sql": """SELECT p.player_name,
       strftime('%Y', m.match_date) as year,
       AVG(pmp.runs_scored) as avg_runs_per_match,
       AVG(pmp.strike_rate) as avg_strike_rate
FROM players p
JOIN player_match_performance pmp ON p.player_id = pmp.player_id
JOIN matches m ON pmp.match_id = m.match_id
WHERE m.match_date >= '2024-01-01'
GROUP BY p.player_id, p.player_name, strftime('%Y', m.match_date)
HAVING COUNT(pmp.match_id) >= 1
ORDER BY p.player_name, year;"""
        },
        {
            "title": "All-rounder effectiveness",
            "difficulty": "Advanced",
            "description": "Evaluate all-rounders based on both batting and bowling contributions.",
            "sql": """SELECT p.player_name, 
       p.batting_average, p.bowling_average, p.runs_scored, p.wickets_taken,
       CASE 
         WHEN p.bowling_average > 0 THEN ROUND(p.batting_average / p.bowling_average, 2)
         ELSE p.batting_average 
       END as effectiveness_ratio
FROM players p
WHERE p.wickets_taken > 5 AND p.runs_scored > 500
ORDER BY effectiveness_ratio DESC;"""
        }
    ]

def display_about_section():
    """Display information about SQL Analytics"""
    st.markdown("---")
    st.markdown("### ℹ️ About SQL Analytics")

    # Query difficulty breakdown
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 🟢 Beginner (8 queries)
        - Basic SELECT, WHERE, GROUP BY
        - Simple JOINs and aggregations
        - Fundamental cricket statistics
        - Perfect for SQL beginners
        """)

    with col2:
        st.markdown("""
        #### 🟡 Intermediate (8 queries)
        - Complex JOINs and subqueries  
        - CASE statements and conditions
        - Multi-table analysis
        - Performance comparisons
        """)

    with col3:
        st.markdown("""
        #### 🔴 Advanced (9 queries)
        - Statistical calculations
        - Complex aggregations
        - Performance analysis
        - Comprehensive insights
        """)

    # Usage instructions
    st.markdown("### 🎯 How to Use")
    st.info("""
    **Step-by-step Guide:**
    1. **Initialize Database** - Click the 'Initialize Sample Database' button first
    2. **Select a Query** - Choose from 25 practice queries using the dropdown
    3. **Review the Question** - Read the description to understand the query goal
    4. **Execute** - Click "Execute Query" to run against the sample cricket database
    5. **Analyze Results** - Review the output table and statistics
    6. **Download** - Export results as CSV for further analysis

    **Database Schema:**
    - **teams**: Team information and details
    - **players**: Player profiles and career statistics  
    - **matches**: Match details and results
    - **venues**: Stadium and ground information
    - **series**: Tournament and series data
    - **player_match_performance**: Individual match performance data
    """)

if __name__ == "__main__":
    show()
