"""
Database Connection and Schema Management
Handles SQLite database operations and table creation
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime
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

def check_db_connection():
    """Check if database connection is working"""
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        return False
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False

def init_database():
    """Initialize database with all required tables"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Create Teams table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY,
                team_name TEXT UNIQUE NOT NULL,
                team_sname TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Players table  
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        """)

        # Insert sample data
        insert_sample_data(cursor)

        conn.commit()
        logger.info("Database initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def insert_sample_data(cursor):
    """Insert sample data for testing"""
    try:
        # Sample teams
        teams_data = [
            (1, 'India', 'IND', 'India'),
            (2, 'Australia', 'AUS', 'Australia'), 
            (3, 'England', 'ENG', 'England'),
            (4, 'Pakistan', 'PAK', 'Pakistan')
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO teams (team_id, team_name, team_sname, country) 
            VALUES (?, ?, ?, ?)
        """, teams_data)

        # Sample players
        players_data = [
            (1, 'Virat Kohli', 1, 'Batsman', 'Right-handed', '', 'Indian', 
             '1988-11-05', 254, 12169, 0, 49.95, 0.0, 81.5, 0.0),
            (2, 'Rohit Sharma', 1, 'Batsman', 'Right-handed', '', 'Indian', 
             '1987-04-30', 227, 9205, 0, 42.25, 0.0, 83.6, 0.0),
            (3, 'Steve Smith', 2, 'Batsman', 'Right-handed', '', 'Australian', 
             '1989-06-02', 128, 4378, 1, 43.34, 77.0, 82.1, 5.5)
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO players 
            (player_id, player_name, team_id, role, batting_style, bowling_style, 
             nationality, date_of_birth, matches_played, runs_scored, wickets_taken, 
             batting_average, bowling_average, strike_rate, economy_rate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, players_data)

    except Exception as e:
        logger.error(f"Sample data insertion error: {e}")

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

def execute_update(query, params=None):
    """Execute an UPDATE/INSERT/DELETE query"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Update execution error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
