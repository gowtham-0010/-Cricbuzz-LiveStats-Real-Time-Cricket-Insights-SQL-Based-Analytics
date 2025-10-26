"""
Enhanced Player Data Fetcher - INCREMENTAL & CLEAN VERSION
Features:
- Incremental updates (add more players each run)
- No duplicates (skips already fetched)
- Commits after each player (safe to stop anytime)
- Real data only from Cricbuzz API
"""

import requests
import time
import sqlite3
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CricbuzzPlayerAPI:
    """Player data fetcher with incremental update capability"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://cricbuzz-cricket.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting and error handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            time.sleep(0.5)  # Rate limiting
            response = self.session.get(url, params=params, timeout=15)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return self.make_api_request(endpoint, params)
            else:
                logger.error(f"API error {response.status_code} for {endpoint}")
                return None
        except Exception as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None

    def get_all_international_teams(self) -> Optional[List[Dict]]:
        """Fetch all international cricket teams"""
        data = self.make_api_request("teams/v1/international")
        return data["list"] if data and "list" in data else None

    def get_team_players(self, team_id: int) -> Optional[List[Dict]]:
        """Fetch all players for a specific team"""
        data = self.make_api_request(f"teams/v1/{team_id}/players")
        return data["player"] if data and "player" in data else None

    def get_player_info(self, player_id: str) -> Optional[Dict]:
        """Fetch detailed player information"""
        return self.make_api_request(f"stats/v1/player/{player_id}")

    def extract_player_stats(self, player_data: Dict) -> Optional[Dict]:
        """Extract real player statistics from API response"""
        if not player_data:
            return None

        try:
            return {
                "profile": {
                    "name": player_data.get("name"),
                    "nickName": player_data.get("nickName"),
                    "role": player_data.get("role"),
                    "bat": player_data.get("bat"),
                    "bowl": player_data.get("bowl"),
                    "birthPlace": player_data.get("birthPlace"),
                    "DoB": player_data.get("DoB"),
                    "intlTeam": player_data.get("intlTeam"),
                    "teams": player_data.get("teams"),
                    "bio": player_data.get("bio", "")[:1000],
                    "image": player_data.get("image")
                },
                "has_stats": True
            }
        except Exception as e:
            logger.error(f"Error extracting stats: {e}")
            return None

    def determine_player_role(self, batting_style: str, bowling_style: str, player_name: str) -> str:
        """Intelligently determine player role"""
        name_lower = player_name.lower()

        if any(kw in name_lower for kw in ["wicket", "keeper"]):
            return "Wicket-keeper"

        if batting_style and bowling_style:
            return "All-rounder"

        if bowling_style and any(kw in bowling_style.lower() for kw in ["fast", "medium", "spin", "off", "leg"]):
            return "Bowler"

        return "Batsman"

    def build_player_database(self, db_path: str = "data/cricbuzz.db") -> int:
        """
        Build/update player database incrementally
        - Skips already fetched players
        - Commits after each player
        - Safe to stop anytime
        """
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Create table if not exists (incremental - don't drop!)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players_real (
                    player_id TEXT PRIMARY KEY,
                    player_name TEXT NOT NULL,
                    nick_name TEXT,
                    team_id INTEGER,
                    team_name TEXT,
                    role TEXT,
                    batting_style TEXT,
                    bowling_style TEXT,
                    date_of_birth TEXT,
                    birth_place TEXT,
                    international_team TEXT,
                    teams_played TEXT,
                    bio TEXT,
                    image_url TEXT,
                    image_id INTEGER,
                    has_detailed_stats BOOLEAN DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            total_added = 0
            detailed_added = 0
            skipped = 0

            # Get all teams
            teams = self.get_all_international_teams()
            if not teams:
                logger.error("Failed to fetch teams")
                return 0

            logger.info(f"Processing {len(teams)} teams...")

            for team in teams:
                if not isinstance(team, dict) or "teamId" not in team:
                    continue

                team_id = team["teamId"]
                team_name = team.get("teamName", "Unknown")

                logger.info(f"\n{'='*60}")
                logger.info(f"Team: {team_name} (ID: {team_id})")
                logger.info(f"{'='*60}")

                # Get players
                players = self.get_team_players(team_id)
                if not players:
                    logger.warning(f"No players found for {team_name}")
                    continue

                for player in players:
                    if not isinstance(player, dict) or "id" not in player:
                        continue

                    player_id = player.get("id")
                    player_name = player.get("name", "Unknown")

                    # Skip if already has detailed stats
                    cursor.execute("""
                        SELECT has_detailed_stats FROM players_real WHERE player_id = ?
                    """, (player_id,))

                    existing = cursor.fetchone()
                    if existing and existing[0] == 1:
                        logger.info(f"⏭️  {player_name} - Already has detailed stats")
                        skipped += 1
                        continue

                    # Process player
                    batting_style = player.get("battingStyle", "")
                    bowling_style = player.get("bowlingStyle", "")
                    image_id = player.get("imageId", 0)
                    role = self.determine_player_role(batting_style, bowling_style, player_name)

                    # Insert/update basic info
                    cursor.execute("""
                        INSERT OR REPLACE INTO players_real 
                        (player_id, player_name, team_id, team_name, role,
                         batting_style, bowling_style, image_id, has_detailed_stats, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
                    """, (player_id, player_name, team_id, team_name, role,
                          batting_style, bowling_style, image_id))

                    conn.commit()  # Commit after INSERT
                    total_added += 1
                    logger.info(f"✅ {player_name} ({player_id}) - {role}")

                    # Fetch detailed stats
                    logger.info(f"   📊 Fetching detailed stats...")
                    player_detail = self.get_player_info(player_id)

                    if player_detail:
                        stats = self.extract_player_stats(player_detail)

                        if stats and stats.get("has_stats"):
                            profile = stats["profile"]

                            # Update with detailed info
                            cursor.execute("""
                                UPDATE players_real 
                                SET nick_name = ?,
                                    date_of_birth = ?,
                                    birth_place = ?,
                                    international_team = ?,
                                    teams_played = ?,
                                    bio = ?,
                                    image_url = ?,
                                    has_detailed_stats = 1,
                                    last_updated = CURRENT_TIMESTAMP
                                WHERE player_id = ?
                            """, (
                                profile.get("nickName"),
                                profile.get("DoB"),
                                profile.get("birthPlace"),
                                profile.get("intlTeam"),
                                profile.get("teams"),
                                profile.get("bio"),
                                profile.get("image"),
                                player_id
                            ))

                            conn.commit()  # Commit after UPDATE
                            detailed_added += 1
                            logger.info(f"   ✅ Stored detailed stats")
                        else:
                            logger.info(f"   ℹ️  No detailed stats available")
                    else:
                        logger.info(f"   ℹ️  Could not fetch from API")

                    time.sleep(0.3)  # Rate limiting

                logger.info(f"✅ Completed {team_name}")

            conn.commit()  # Final commit

            logger.info(f"\n{'='*60}")
            logger.info(f"✅ SYNC COMPLETED")
            logger.info(f"   Players processed: {total_added}")
            logger.info(f"   With detailed stats: {detailed_added}")
            logger.info(f"   Skipped (already fetched): {skipped}")
            logger.info(f"{'='*60}")

            return total_added

        except Exception as e:
            logger.error(f"Database error: {e}")
            logger.exception("Full error:")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def search_players_by_name(self, player_name: str, db_path: str = "data/cricbuzz.db") -> List[Dict]:
        """Search for players by name"""
        if not os.path.exists(db_path):
            return []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            search_term = f"%{player_name.lower()}%"
            cursor.execute("""
                SELECT player_id, player_name, team_name, role, 
                       batting_style, bowling_style, international_team, image_id,
                       has_detailed_stats, nick_name
                FROM players_real 
                WHERE LOWER(player_name) LIKE ? 
                ORDER BY has_detailed_stats DESC, player_name
                LIMIT 20
            """, (search_term,))

            players = []
            for row in cursor.fetchall():
                players.append({
                    "id": row[0],
                    "name": row[1],
                    "teamName": row[2],
                    "role": row[3],
                    "battingStyle": row[4],
                    "bowlingStyle": row[5],
                    "nationality": row[6] or row[2],
                    "imageId": row[7],
                    "hasDetailedStats": bool(row[8]),
                    "nickName": row[9]
                })

            return players
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
        finally:
            conn.close()

    def get_player_stats(self, player_id: str, db_path: str = "data/cricbuzz.db") -> Optional[Dict]:
        """Get player statistics from database"""
        if not os.path.exists(db_path):
            return None

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT player_name, nick_name, role, batting_style, bowling_style,
                       date_of_birth, birth_place, international_team,
                       teams_played, bio, image_url, team_name, has_detailed_stats
                FROM players_real WHERE player_id = ?
            """, (player_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "profile": {
                    "name": row[0],
                    "nickName": row[1],
                    "role": row[2],
                    "battingStyle": row[3],
                    "bowlingStyle": row[4],
                    "dateOfBirth": row[5],
                    "birthPlace": row[6],
                    "internationalTeam": row[7],
                    "teamsPlayed": row[8],
                    "bio": row[9],
                    "imageUrl": row[10],
                    "nationality": row[11]
                },
                "hasDetailedStats": bool(row[12])
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return None
        finally:
            conn.close()


# Convenience functions
def initialize_database(api_key: str, db_path: str = "data/cricbuzz.db") -> int:
    """Initialize/update database with real player data"""
    api = CricbuzzPlayerAPI(api_key)
    return api.build_player_database(db_path)


def search_player(player_name: str, api_key: str = "dummy") -> List[Dict]:
    """Search for players"""
    api = CricbuzzPlayerAPI(api_key)
    return api.search_players_by_name(player_name)


def get_player_info(player_id: str, api_key: str = "dummy") -> Optional[Dict]:
    """Get player information"""
    api = CricbuzzPlayerAPI(api_key)
    return api.get_player_stats(player_id)


if __name__ == "__main__":
    API_KEY = "d9ce22edb5msh7f4ea8ba68cf789p19cd33jsn543e73adfde7"
    print("Testing Player Data Fetcher...")
    initialize_database(API_KEY)
