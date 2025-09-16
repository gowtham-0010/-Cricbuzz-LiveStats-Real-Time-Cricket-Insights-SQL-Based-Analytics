"""
Cricbuzz API Data Fetcher - FINAL FIXED VERSION
Handles non-numeric player IDs and scorecard data structure properly
"""

import requests
import sqlite3
import pandas as pd
import json
import time
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import sys
from tqdm import tqdm
import hashlib

# Setup enhanced logging with real-time display
class RealTimeFormatter(logging.Formatter):
    """Custom formatter for real-time status updates"""

    def format(self, record):
        timestamp = datetime.now().strftime('%H:%M:%S')
        if record.levelname == 'INFO':
            return f"\033[32m[{timestamp}] ✅ {record.getMessage()}\033[0m"
        elif record.levelname == 'WARNING':
            return f"\033[33m[{timestamp}] ⚠️  {record.getMessage()}\033[0m"
        elif record.levelname == 'ERROR':
            return f"\033[31m[{timestamp}] ❌ {record.getMessage()}\033[0m"
        else:
            return f"[{timestamp}] {record.getMessage()}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set custom formatter
for handler in logger.handlers:
    handler.setFormatter(RealTimeFormatter())

class CricbuzzDataFetcher:
    """Final fixed fetcher with proper player ID handling"""

    def __init__(self, api_key: str, db_path: str = 'data/cricbuzz.db'):
        self.api_key = api_key
        self.base_url = "https://cricbuzz-cricket.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
        }
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Statistics tracking
        self.stats = {
            'api_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'teams_stored': 0,
            'players_stored': 0,
            'matches_stored': 0,
            'venues_stored': 0,
            'performances_stored': 0,
            'start_time': None,
            'current_operation': 'Initializing'
        }

        # Create database directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self.print_header("🗄️ DATABASE INITIALIZATION")
        self.init_database()

    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n\033[36m{'=' * 60}\033[0m")
        print(f"\033[36m{title.center(60)}\033[0m")
        print(f"\033[36m{'=' * 60}\033[0m")

    def print_status(self, message: str, level: str = 'info'):
        """Print formatted status message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        if level == 'success':
            print(f"\033[32m[{timestamp}] ✅ {message}\033[0m")
        elif level == 'warning':
            print(f"\033[33m[{timestamp}] ⚠️  {message}\033[0m")
        elif level == 'error':
            print(f"\033[31m[{timestamp}] ❌ {message}\033[0m")
        elif level == 'progress':
            print(f"\033[34m[{timestamp}] 🔄 {message}\033[0m")
        else:
            print(f"[{timestamp}] ℹ️  {message}")

    def generate_player_id(self, player_key: str, player_name: str, team_id: int) -> int:
        """Generate a consistent numeric player ID from non-numeric keys"""
        # Create a unique string combining all identifiers
        unique_string = f"{player_key}_{player_name}_{team_id}"
        # Generate a hash and convert to integer
        hash_obj = hashlib.md5(unique_string.encode())
        # Take first 8 characters of hex and convert to int
        player_id = int(hash_obj.hexdigest()[:8], 16)
        # Ensure it's positive and within reasonable range
        return abs(player_id) % 999999999 + 1000000

    def make_api_request(self, endpoint: str, params: Dict = None, description: str = "") -> Optional[Dict]:
        """Enhanced API request with real-time status"""
        self.stats['api_calls'] += 1

        try:
            url = f"{self.base_url}{endpoint}"

            # Show request details
            self.print_status(f"Making API call to: {endpoint}", 'progress')
            if description:
                self.print_status(f"Purpose: {description}")

            time.sleep(1)  # Rate limiting

            response = self.session.get(url, params=params, timeout=15)

            if response.status_code == 200:
                self.stats['successful_calls'] += 1
                data = response.json()

                # Show response size
                data_size = len(str(data)) if data else 0
                self.print_status(f"Success! Response size: {data_size:,} characters", 'success')

                return data

            elif response.status_code == 429:
                self.stats['failed_calls'] += 1
                self.print_status("Rate limit exceeded, waiting 60 seconds...", 'warning')

                # Countdown timer
                for i in range(60, 0, -1):
                    print(f"\r\033[33m⏳ Waiting {i:2d} seconds for rate limit reset...\033[0m", end='', flush=True)
                    time.sleep(1)
                print()  # New line

                return self.make_api_request(endpoint, params, description)  # Retry
            else:
                self.stats['failed_calls'] += 1
                self.print_status(f"API request failed: {response.status_code} - {response.text[:100]}", 'error')
                return None

        except requests.exceptions.RequestException as e:
            self.stats['failed_calls'] += 1
            self.print_status(f"Network error: {e}", 'error')
            return None
        except Exception as e:
            self.stats['failed_calls'] += 1
            self.print_status(f"Unexpected error: {e}", 'error')
            return None

    def init_database(self):
        """Initialize database with corrected schema"""
        self.stats['current_operation'] = 'Initializing Database Schema'

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Teams table
            self.print_status("Creating table: teams")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    team_id INTEGER PRIMARY KEY,
                    team_name TEXT UNIQUE NOT NULL,
                    team_sname TEXT,
                    country TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.print_status("Table 'teams' created successfully", 'success')

            # Venues table
            self.print_status("Creating table: venues")
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
            self.print_status("Table 'venues' created successfully", 'success')

            # Series table
            self.print_status("Creating table: series")
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
            self.print_status("Table 'series' created successfully", 'success')

            # Matches table
            self.print_status("Creating table: matches")
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
            self.print_status("Table 'matches' created successfully", 'success')

            # Players table
            self.print_status("Creating table: players")
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
        player_key TEXT,                 -- Added column
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team_id) REFERENCES teams (team_id)
    )
""")
            self.print_status("Table 'players' created successfully", 'success')

            # Player match performance table
            self.print_status("Creating table: player_match_performance")
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
    fours INTEGER DEFAULT 0,
    sixes INTEGER DEFAULT 0,
    overs_bowled REAL DEFAULT 0.0,
    wickets_taken INTEGER DEFAULT 0,
    runs_conceded INTEGER DEFAULT 0,
    economy_rate REAL DEFAULT 0.0,
    maidens INTEGER DEFAULT 0,
    out_desc TEXT,
    player_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_id, player_id, innings_number),
    FOREIGN KEY (player_id) REFERENCES players (player_id),
    FOREIGN KEY (match_id) REFERENCES matches (match_id),
    FOREIGN KEY (team_id) REFERENCES teams (team_id)
  )
""")

            self.print_status("Table 'player_match_performance' created successfully", 'success')

            # Team statistics table
            self.print_status("Creating table: team_statistics")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_statistics (
                    stat_id INTEGER PRIMARY KEY,
                    team_id INTEGER,
                    matches_played INTEGER DEFAULT 0,
                    matches_won INTEGER DEFAULT 0,
                    matches_lost INTEGER DEFAULT 0,
                    matches_drawn INTEGER DEFAULT 0,
                    matches_tied INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams (team_id)
                )
            """)
            self.print_status("Table 'team_statistics' created successfully", 'success')

            conn.commit()
            self.print_status("Database schema initialized successfully!", 'success')

        except Exception as e:
            self.print_status(f"Database initialization error: {e}", 'error')
            conn.rollback()
        finally:
            conn.close()

    def fetch_and_store_all_data(self):
        """Main method with enhanced progress tracking"""
        self.stats['start_time'] = datetime.now()

        try:
            # Step 1: Recent matches
            self.print_header("📡 FETCHING RECENT MATCHES")
            self.stats['current_operation'] = 'Fetching Recent Matches'
            self.fetch_recent_matches()

            # Step 2: Live matches  
            self.print_header("🔴 FETCHING LIVE MATCHES")
            self.stats['current_operation'] = 'Fetching Live Matches'
            self.fetch_live_matches()

            # Step 3: Teams data
            self.print_header("🏏 PROCESSING TEAMS DATA")
            self.stats['current_operation'] = 'Processing Teams Data'
            self.fetch_teams_data()

            # Step 4: Detailed scorecards
            self.print_header("📊 FETCHING MATCH SCORECARDS")
            self.stats['current_operation'] = 'Fetching Detailed Scorecards'
            self.fetch_match_scorecards()

            # Step 5: Update player statistics
            self.print_header("👤 UPDATING PLAYER STATISTICS")
            self.stats['current_operation'] = 'Calculating Player Statistics'
            self.update_player_statistics()

            # Step 6: Update team statistics
            self.print_header("🏆 UPDATING TEAM STATISTICS")
            self.stats['current_operation'] = 'Calculating Team Statistics'
            self.update_team_statistics()

            self.stats['current_operation'] = 'Completed Successfully'
            self.print_header("🎉 DATA FETCH COMPLETED")

        except Exception as e:
            self.print_status(f"Error in data fetch process: {e}", 'error')

    def fetch_recent_matches(self):
        """Fetch recent matches with detailed progress"""
        endpoint = "/matches/v1/recent"
        data = self.make_api_request(endpoint, description="Fetching recent cricket matches")

        if not data or 'typeMatches' not in data:
            self.print_status("No recent matches data found", 'warning')
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            total_type_matches = len(data['typeMatches'])
            self.print_status(f"Processing {total_type_matches} match types")

            for type_idx, type_match in enumerate(data['typeMatches'], 1):
                match_type = type_match.get('matchType', 'Unknown')
                self.print_status(f"[{type_idx}/{total_type_matches}] Processing {match_type} matches", 'progress')

                if 'seriesMatches' not in type_match:
                    continue

                series_count = len(type_match['seriesMatches'])
                self.print_status(f"Found {series_count} series in {match_type}")

                for series_idx, series_match in enumerate(type_match['seriesMatches'], 1):
                    if 'seriesAdWrapper' not in series_match:
                        continue

                    series_info = series_match['seriesAdWrapper']
                    series_name = series_info.get('seriesName', 'Unknown Series')

                    self.print_status(f"  [{series_idx}/{series_count}] Processing series: {series_name}")

                    # Store series information
                    series_id = series_info.get('seriesId')
                    cursor.execute("""
                        INSERT OR IGNORE INTO series (series_id, series_name)
                        VALUES (?, ?)
                    """, (series_id, series_name))

                    # Process matches in this series
                    if 'matches' in series_info:
                        matches = series_info['matches']
                        match_count = len(matches)
                        self.print_status(f"    Processing {match_count} matches in {series_name}")

                        for match_idx, match in enumerate(matches, 1):
                            match_desc = match.get('matchInfo', {}).get('matchDesc', f'Match {match_idx}')
                            self.print_status(f"    [{match_idx}/{match_count}] {match_desc}")
                            self.store_match_data(cursor, match, series_id)
                            self.stats['matches_stored'] += 1

            conn.commit()
            self.print_status(f"Recent matches stored successfully! Total: {self.stats['matches_stored']}", 'success')

        except Exception as e:
            self.print_status(f"Error storing recent matches: {e}", 'error')
            conn.rollback()
        finally:
            conn.close()

    def fetch_live_matches(self):
        """Fetch live matches"""
        endpoint = "/matches/v1/live"
        data = self.make_api_request(endpoint, description="Fetching current live matches")

        if not data or 'typeMatches' not in data:
            self.print_status("No live matches found", 'warning')
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            live_count = 0
            for type_match in data['typeMatches']:
                if 'seriesMatches' not in type_match:
                    continue

                for series_match in type_match['seriesMatches']:
                    if 'seriesAdWrapper' not in series_match:
                        continue

                    series_info = series_match['seriesAdWrapper']
                    series_id = series_info.get('seriesId')

                    if 'matches' in series_info:
                        for match in series_info['matches']:
                            match_desc = match.get('matchInfo', {}).get('matchDesc', 'Live Match')
                            self.print_status(f"🔴 LIVE: {match_desc}")
                            self.store_match_data(cursor, match, series_id, is_live=True)
                            live_count += 1

            conn.commit()
            self.print_status(f"Live matches processed: {live_count}", 'success')

        except Exception as e:
            self.print_status(f"Error storing live matches: {e}", 'error')
            conn.rollback()
        finally:
            conn.close()

    def store_match_data(self, cursor, match_data: Dict, series_id: int, is_live: bool = False):
        """Store match data"""
        try:
            match_info = match_data.get('matchInfo', {})
            match_id = match_info.get('matchId')

            if not match_id:
                return

            # Extract team information
            team1_info = match_info.get('team1', {})
            team2_info = match_info.get('team2', {})

            team1_id = team1_info.get('teamId')
            team2_id = team2_info.get('teamId')

            # Store teams
            if team1_id:
                team1_name = team1_info.get('teamName', 'Unknown Team')
                cursor.execute("""
                    INSERT OR IGNORE INTO teams (team_id, team_name, team_sname)
                    VALUES (?, ?, ?)
                """, (team1_id, team1_name, team1_info.get('teamSName')))

            if team2_id:
                team2_name = team2_info.get('teamName', 'Unknown Team')
                cursor.execute("""
                    INSERT OR IGNORE INTO teams (team_id, team_name, team_sname)
                    VALUES (?, ?, ?)
                """, (team2_id, team2_name, team2_info.get('teamSName')))

            # Store venue information
            venue_info = match_info.get('venueInfo', {})
            venue_id = venue_info.get('id')

            if venue_id:
                venue_name = venue_info.get('ground', 'Unknown Venue')
                cursor.execute("""
                    INSERT OR IGNORE INTO venues (venue_id, venue_name, city)
                    VALUES (?, ?, ?)
                """, (venue_id, venue_name, venue_info.get('city')))

            # Convert timestamp to date
            start_date_ts = match_info.get('startDate')
            match_date = None
            if start_date_ts:
                try:
                    match_date = datetime.fromtimestamp(int(start_date_ts) / 1000).date()
                except:
                    pass

            # Determine match status
            match_status = 'Live' if is_live else match_info.get('stateTitle', 'Completed')

            # Store match information
            cursor.execute("""
                INSERT OR REPLACE INTO matches (
                    match_id, match_desc, match_format, match_date, series_id,
                    team1_id, team2_id, venue_id, match_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                match_info.get('matchDesc'),
                match_info.get('matchFormat'),
                match_date,
                series_id,
                team1_id,
                team2_id,
                venue_id,
                match_status
            ))

        except Exception as e:
            self.print_status(f"Error storing match {match_id}: {e}", 'error')

    def fetch_teams_data(self):
        """Update teams with country information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT team_id, team_name FROM teams")
            teams = cursor.fetchall()

            self.print_status(f"Updating country information for {len(teams)} teams")

            for idx, (team_id, team_name) in enumerate(teams, 1):
                country = self.determine_country_from_team_name(team_name)
                cursor.execute("UPDATE teams SET country = ? WHERE team_id = ?", (country, team_id))
                self.print_status(f"[{idx:2d}/{len(teams)}] {team_name} → {country}")

            conn.commit()
            self.print_status("Teams data updated successfully", 'success')

        except Exception as e:
            self.print_status(f"Error updating teams data: {e}", 'error')
            conn.rollback()
        finally:
            conn.close()

    def determine_country_from_team_name(self, team_name: str) -> str:
        """Determine country from team name"""
        country_mapping = {
            'india': 'India', 'australia': 'Australia', 'england': 'England', 'pakistan': 'Pakistan',
            'south africa': 'South Africa', 'new zealand': 'New Zealand', 'sri lanka': 'Sri Lanka',
            'bangladesh': 'Bangladesh', 'afghanistan': 'Afghanistan', 'west indies': 'West Indies',
            'ireland': 'Ireland', 'scotland': 'Scotland', 'netherlands': 'Netherlands',
            'zimbabwe': 'Zimbabwe', 'hong kong': 'Hong Kong', 'uae': 'United Arab Emirates',
            'united arab emirates': 'United Arab Emirates'
        }

        team_lower = team_name.lower()
        for key, value in country_mapping.items():
            if key in team_lower:
                return value

        return team_name

    def fetch_match_scorecards(self):
        """FIXED: Fetch scorecards with proper player ID handling"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT DISTINCT m.match_id, m.match_desc 
                FROM matches m 
                LEFT JOIN player_match_performance pmp ON m.match_id = pmp.match_id
                WHERE pmp.match_id IS NULL
                ORDER BY m.match_date DESC
                LIMIT 3
            """)

            matches_to_fetch = cursor.fetchall()
            total_matches = len(matches_to_fetch)

            if total_matches == 0:
                self.print_status("No new matches to fetch scorecards for", 'warning')
                return

            self.print_status(f"Fetching scorecards for {total_matches} matches")

            with tqdm(matches_to_fetch, desc="Fetching Scorecards", unit="match") as pbar:
                for match_id, match_desc in pbar:
                    pbar.set_description(f"Fetching: {match_desc[:30]}...")

                    endpoint = f"/mcenter/v1/{match_id}/hscard"
                    scorecard_data = self.make_api_request(endpoint, 
                                                        description=f"Scorecard for {match_desc}")

                    if scorecard_data:
                        players_added = self.store_scorecard_data_fixed(cursor, match_id, scorecard_data)
                        self.print_status(f"✅ {match_desc}: Added {players_added} player performances", 'success')
                    else:
                        self.print_status(f"⚠️  No scorecard data for: {match_desc}", 'warning')

                    time.sleep(2)

            conn.commit()
            self.print_status("Scorecards processing completed", 'success')

        except Exception as e:
            self.print_status(f"Error fetching scorecards: {e}", 'error')
            conn.rollback()
        finally:
            conn.close()

    def store_scorecard_data_fixed(self, cursor, match_id: int, scorecard_data: Dict) -> int:
        """FIXED: Store scorecard data with proper player ID handling"""
        players_added = 0

        try:
            if 'scoreCard' not in scorecard_data:
                self.print_status("No scoreCard in response", 'warning')
                return 0

            innings_list = scorecard_data['scoreCard']
            self.print_status(f"Processing {len(innings_list)} innings")

            for innings_num, innings_data in enumerate(innings_list, 1):
                self.print_status(f"Processing innings {innings_num}")

                if 'batTeamDetails' not in innings_data:
                    self.print_status("No batTeamDetails found", 'warning')
                    continue

                bat_team_details = innings_data['batTeamDetails']
                bat_team_id = bat_team_details.get('batTeamId')

                if 'batsmenData' in bat_team_details:
                    batsmen_data = bat_team_details['batsmenData']
                    self.print_status(f"Found {len(batsmen_data)} batsmen")

                    for player_key, player_data in batsmen_data.items():
                        if not isinstance(player_data, dict):
                            continue

                        # FIXED: Handle non-numeric player keys
                        player_name = player_data.get('batName', f'Player_{player_key}')

                        # Generate consistent numeric player ID
                        numeric_player_id = self.generate_player_id(player_key, player_name, bat_team_id)

                        # Store player with generated ID
                        cursor.execute("""
                            INSERT OR IGNORE INTO players (player_id, player_name, team_id, role, player_key)
                            VALUES (?, ?, ?, ?, ?)
                        """, (numeric_player_id, player_name, bat_team_id, 'Batsman', player_key))

                        # Store performance data
                        cursor.execute("""
  INSERT INTO player_match_performance (
    player_id, match_id, team_id, innings_number,
    batting_order, runs_scored, balls_faced,
    strike_rate, fours, sixes, out_desc, player_key
  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  ON CONFLICT(match_id, player_id, innings_number) DO UPDATE SET
    runs_scored   = excluded.runs_scored,
    balls_faced   = excluded.balls_faced,
    strike_rate   = excluded.strike_rate,
    fours         = excluded.fours,
    sixes         = excluded.sixes,
    out_desc      = excluded.out_desc
""", (
  numeric_player_id, match_id, team_id, innings_num,
  player_data.get('batOrder', 0), player_data.get('runs', 0),
  player_data.get('balls', 0), player_data.get('strikeRate', 0.0),
  player_data.get('fours', 0), player_data.get('sixes', 0),
  player_data.get('outDesc', ''), player_key
))


                        players_added += 1
                        self.stats['performances_stored'] += 1
                        self.stats['players_stored'] += 1

                        self.print_status(f"Added batsman: {player_name} (ID: {numeric_player_id})")

                # Process bowling data
                if 'bowlTeamDetails' in innings_data:
                    bowl_team_details = innings_data['bowlTeamDetails']
                    bowl_team_id = bowl_team_details.get('bowlTeamId')

                    if 'bowlersData' in bowl_team_details:
                        bowlers_data = bowl_team_details['bowlersData']
                        self.print_status(f"Found {len(bowlers_data)} bowlers")

                        for bowler_key, bowler_data in bowlers_data.items():
                            if not isinstance(bowler_data, dict):
                                continue

                            # FIXED: Handle non-numeric bowler keys
                            bowler_name = bowler_data.get('bowlName', f'Bowler_{bowler_key}')

                            # Generate consistent numeric bowler ID
                            numeric_bowler_id = self.generate_player_id(bowler_key, bowler_name, bowl_team_id)

                            # Store bowler
                            cursor.execute("""
                                INSERT OR IGNORE INTO players (player_id, player_name, team_id, role, player_key)
                                VALUES (?, ?, ?, ?, ?)
                            """, (numeric_bowler_id, bowler_name, bowl_team_id, 'Bowler', bowler_key))

                            # Update bowling performance
                            cursor.execute("""
                                INSERT OR IGNORE INTO player_match_performance (
                                    player_id, match_id, team_id, innings_number, player_key
                                ) VALUES (?, ?, ?, ?, ?)
                            """, (numeric_bowler_id, match_id, bowl_team_id, innings_num, bowler_key))

                            cursor.execute("""
                                UPDATE player_match_performance 
                                SET overs_bowled = ?, wickets_taken = ?, runs_conceded = ?, 
                                    economy_rate = ?, maidens = ?
                                WHERE player_id = ? AND match_id = ? AND innings_number = ?
                            """, (
                                bowler_data.get('overs', 0.0), bowler_data.get('wickets', 0),
                                bowler_data.get('runs', 0), bowler_data.get('economy', 0.0),
                                bowler_data.get('maidens', 0), numeric_bowler_id, match_id, innings_num
                            ))

                            players_added += 1
                            self.stats['performances_stored'] += 1

                            self.print_status(f"Added bowler: {bowler_name} (ID: {numeric_bowler_id})")

            return players_added

        except Exception as e:
            self.print_status(f"Error storing scorecard data: {e}", 'error')
            return 0

    def update_player_statistics(self):
        """Update player statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            self.print_status("Calculating batting averages, strike rates, and bowling statistics...")

            cursor.execute("""
                UPDATE players SET
                    matches_played = (
                        SELECT COUNT(DISTINCT match_id) 
                        FROM player_match_performance 
                        WHERE player_id = players.player_id
                    ),
                    runs_scored = (
                        SELECT COALESCE(SUM(runs_scored), 0) 
                        FROM player_match_performance 
                        WHERE player_id = players.player_id
                    ),
                    wickets_taken = (
                        SELECT COALESCE(SUM(wickets_taken), 0) 
                        FROM player_match_performance 
                        WHERE player_id = players.player_id
                    ),
                    batting_average = (
                        SELECT CASE 
                            WHEN COUNT(*) > 0 THEN ROUND(CAST(SUM(runs_scored) AS FLOAT) / COUNT(*), 2)
                            ELSE 0.0 
                        END
                        FROM player_match_performance 
                        WHERE player_id = players.player_id AND runs_scored > 0
                    ),
                    strike_rate = (
                        SELECT CASE 
                            WHEN SUM(balls_faced) > 0 THEN ROUND(CAST(SUM(runs_scored) AS FLOAT) * 100 / SUM(balls_faced), 2)
                            ELSE 0.0 
                        END
                        FROM player_match_performance 
                        WHERE player_id = players.player_id AND balls_faced > 0
                    ),
                    updated_at = CURRENT_TIMESTAMP
            """)

            conn.commit()
            self.print_status("Player statistics updated successfully", 'success')

        except Exception as e:
            self.print_status(f"Error updating player statistics: {e}", 'error')
            conn.rollback()
        finally:
            conn.close()

    def update_team_statistics(self):
        """Update team statistics with proper null handling"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT team_id, team_name FROM teams")
            teams = cursor.fetchall()

            self.print_status(f"Calculating statistics for {len(teams)} teams")

            for idx, (team_id, team_name) in enumerate(teams, 1):
                cursor.execute("""
                    SELECT 
                        COUNT(*) as matches_played,
                        SUM(CASE WHEN match_winner_id = ? THEN 1 ELSE 0 END) as matches_won
                    FROM matches 
                    WHERE (team1_id = ? OR team2_id = ?) AND match_status = 'Completed'
                """, (team_id, team_id, team_id))

                result = cursor.fetchone()
                matches_played = result[0] if result and result[0] is not None else 0
                matches_won = result[1] if result and result[1] is not None else 0
                matches_lost = matches_played - matches_won

                cursor.execute("""
                    INSERT OR REPLACE INTO team_statistics (
                        team_id, matches_played, matches_won, matches_lost
                    ) VALUES (?, ?, ?, ?)
                """, (team_id, matches_played, matches_won, matches_lost))

                if matches_played > 0:
                    self.print_status(f"[{idx:2d}/{len(teams)}] {team_name}: {matches_won}W-{matches_lost}L ({matches_played} total)")

            conn.commit()
            self.print_status("Team statistics updated successfully", 'success')

        except Exception as e:
            self.print_status(f"Error updating team statistics: {e}", 'error')
            conn.rollback()
        finally:
            conn.close()

    def get_database_summary(self):
        """Get database summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            summary = {}
            tables = ['teams', 'players', 'matches', 'venues', 'series', 'player_match_performance', 'team_statistics']

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                summary[table] = count

            return summary

        except Exception as e:
            self.print_status(f"Error getting database summary: {e}", 'error')
            return {}
        finally:
            conn.close()

def main():
    """Main function"""
    # Configuration
    API_KEY = "8f28ac76efmshbb48e07d1c830fcp1d4ea9jsn3872535caf88"
    DB_PATH = "data/cricbuzz.db"

    # Clear screen and show header
    print("\033[2J\033[H")
    print("\033[35m" + "🏏" * 80 + "\033[0m")
    print("\033[35m" + "CRICBUZZ API DATA FETCHER - FINAL FIXED VERSION".center(80) + "\033[0m")
    print("\033[35m" + "🏏" * 80 + "\033[0m\n")

    try:
        # Initialize fetcher
        fetcher = CricbuzzDataFetcher(API_KEY, DB_PATH)

        # Start data fetching
        fetcher.fetch_and_store_all_data()

        # Final summary
        summary = fetcher.get_database_summary()

        # Display final results
        fetcher.print_header("📊 FINAL DATABASE SUMMARY")

        for table, count in summary.items():
            table_display = table.replace('_', ' ').title()
            print(f"\033[32m{table_display:25}: {count:6,} records\033[0m")

        # Calculate total time
        total_time = (datetime.now() - fetcher.stats['start_time']).total_seconds()

        print(f"\n\033[36m" + "=" * 60 + "\033[0m")
        print(f"\033[36m✅ DATA FETCH COMPLETED SUCCESSFULLY!\033[0m")
        print(f"\033[36m📁 Database: {DB_PATH}\033[0m")
        print(f"\033[36m⏱️  Total Time: {int(total_time//60)}m {int(total_time%60)}s\033[0m")
        print(f"\033[36m📡 API Calls: {fetcher.stats['api_calls']} ({fetcher.stats['successful_calls']} successful)\033[0m")
        print(f"\033[36m🎯 Ready for SQL Analytics!\033[0m")

    except KeyboardInterrupt:
        print("\n\033[33m⚠️  Process interrupted by user\033[0m")
    except Exception as e:
        print(f"\n\033[31m❌ Error during data fetch: {e}\033[0m")

if __name__ == "__main__":
    main()
