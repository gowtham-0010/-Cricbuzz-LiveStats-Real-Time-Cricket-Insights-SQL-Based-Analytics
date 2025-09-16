"""
API Utilities for Cricbuzz Data Fetching
Handles all Cricbuzz API interactions and data processing
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
RAPIDAPI_KEY = "abf7ac9a44msh48322180431133cp14f1e1jsn135bf9217cf5"
RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

# Headers for API requests
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST
}

def check_api_connection():
    """Check if Cricbuzz API is accessible"""
    try:
        url = f"{BASE_URL}/matches/v1/recent"
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"API connection check failed: {e}")
        return False

def make_api_request(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make a request to Cricbuzz API with error handling"""
    try:
        url = f"{BASE_URL}/{endpoint}"

        # Add delay to avoid rate limiting
        time.sleep(0.3)

        response = requests.get(url, headers=HEADERS, params=params, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API request failed with status {response.status_code}: {endpoint}")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"API request timeout for endpoint: {endpoint}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error for {endpoint}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {endpoint}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for {endpoint}: {e}")
        return None

def get_recent_matches() -> Optional[List[Dict]]:
    """Fetch recent matches data"""
    data = make_api_request("matches/v1/recent")
    if not data:
        return None

    try:
        matches = []
        type_matches = data.get('typeMatches', [])

        for type_match in type_matches:
            series_matches = type_match.get('seriesMatches', [])
            for series_match in series_matches:
                series_wrapper = series_match.get('seriesAdWrapper', {})
                match_list = series_wrapper.get('matches', [])

                for match in match_list:
                    match_info = match.get('matchInfo', {})
                    processed_match = {
                        'match_id': match_info.get('matchId'),
                        'match_desc': match_info.get('matchDesc', 'N/A'),
                        'match_format': match_info.get('matchFormat', 'N/A'),
                        'team1': match_info.get('team1', {}).get('teamName', 'Team 1'),
                        'team2': match_info.get('team2', {}).get('teamName', 'Team 2'),
                        'venue': match_info.get('venueInfo', {}).get('ground', 'N/A'),
                        'city': match_info.get('venueInfo', {}).get('city', 'N/A'),
                        'status': match_info.get('status', 'N/A'),
                        'match_date': match_info.get('startDate', 'N/A'),
                        'series_name': series_wrapper.get('seriesName', 'N/A')
                    }
                    matches.append(processed_match)

        return matches[:20]  # Return top 20 matches

    except Exception as e:
        logger.error(f"Error processing recent matches: {e}")
        return None

def get_live_matches() -> Optional[List[Dict]]:
    """Fetch live matches data"""
    data = make_api_request("matches/v1/live")
    if not data:
        return None

    try:
        matches = []
        type_matches = data.get('typeMatches', [])

        for type_match in type_matches:
            series_matches = type_match.get('seriesMatches', [])
            for series_match in series_matches:
                series_wrapper = series_match.get('seriesAdWrapper', {})
                match_list = series_wrapper.get('matches', [])

                for match in match_list:
                    match_info = match.get('matchInfo', {})
                    processed_match = {
                        'match_id': match_info.get('matchId'),
                        'match_desc': match_info.get('matchDesc', 'N/A'),
                        'match_format': match_info.get('matchFormat', 'N/A'),
                        'team1': match_info.get('team1', {}).get('teamName', 'Team 1'),
                        'team2': match_info.get('team2', {}).get('teamName', 'Team 2'),
                        'venue': match_info.get('venueInfo', {}).get('ground', 'N/A'),
                        'city': match_info.get('venueInfo', {}).get('city', 'N/A'),
                        'status': match_info.get('status', 'N/A'),
                        'match_date': match_info.get('startDate', 'N/A'),
                        'series_name': series_wrapper.get('seriesName', 'N/A')
                    }
                    matches.append(processed_match)

        return matches

    except Exception as e:
        logger.error(f"Error processing live matches: {e}")
        return None

def get_upcoming_matches() -> Optional[List[Dict]]:
    """Fetch upcoming matches data"""
    data = make_api_request("matches/v1/upcoming")
    if not data:
        return None

    try:
        matches = []
        type_matches = data.get('typeMatches', [])

        for type_match in type_matches:
            series_matches = type_match.get('seriesMatches', [])
            for series_match in series_matches:
                series_wrapper = series_match.get('seriesAdWrapper', {})
                match_list = series_wrapper.get('matches', [])

                for match in match_list:
                    match_info = match.get('matchInfo', {})
                    processed_match = {
                        'match_id': match_info.get('matchId'),
                        'match_desc': match_info.get('matchDesc', 'N/A'),
                        'match_format': match_info.get('matchFormat', 'N/A'),
                        'team1': match_info.get('team1', {}).get('teamName', 'Team 1'),
                        'team2': match_info.get('team2', {}).get('teamName', 'Team 2'),
                        'venue': match_info.get('venueInfo', {}).get('ground', 'N/A'),
                        'city': match_info.get('venueInfo', {}).get('city', 'N/A'),
                        'status': match_info.get('status', 'N/A'),
                        'match_date': match_info.get('startDate', 'N/A'),
                        'series_name': series_wrapper.get('seriesName', 'N/A')
                    }
                    matches.append(processed_match)

        return matches[:15]  # Return top 15 upcoming matches

    except Exception as e:
        logger.error(f"Error processing upcoming matches: {e}")
        return None

def get_match_scorecard(match_id: str) -> Optional[Dict]:
    """Fetch detailed scorecard for a specific match"""
    data = make_api_request(f"mcenter/v1/{match_id}/hscard")
    if not data:
        return None

    try:
        # Process scorecard data
        scorecard = {
            'match_id': match_id,
            'match_header': data.get('matchHeader', {}),
            'innings': data.get('scoreCard', []),
            'match_info': data.get('matchInfo', {}),
            'venue_info': data.get('venueInfo', {}),
            'players_of_match': data.get('playersOfTheMatch', []),
            'players_of_series': data.get('playersOfTheSeries', [])
        }

        return scorecard

    except Exception as e:
        logger.error(f"Error processing scorecard for match {match_id}: {e}")
        return None

def get_match_commentary(match_id: str) -> Optional[Dict]:
    """Fetch live commentary for a specific match"""
    data = make_api_request(f"mcenter/v1/{match_id}/comm")
    if not data:
        return None

    try:
        commentary = {
            'match_id': match_id,
            'commentary_list': data.get('commentaryList', []),
            'match_header': data.get('matchHeader', {}),
            'innings_scorecard': data.get('miniscore', {})
        }

        return commentary

    except Exception as e:
        logger.error(f"Error processing commentary for match {match_id}: {e}")
        return None

def search_player(player_name: str) -> Optional[List[Dict]]:
    """Search for players by name"""
    # For demo purposes, return mock data since player search endpoint needs specific implementation
    mock_players = [
        {
            'player_id': '1',
            'player_name': 'Virat Kohli',
            'team': 'India',
            'role': 'Batsman',
            'batting_style': 'Right-handed',
            'bowling_style': 'Right-arm medium',
            'nationality': 'Indian'
        },
        {
            'player_id': '2', 
            'player_name': 'Rohit Sharma',
            'team': 'India',
            'role': 'Batsman',
            'batting_style': 'Right-handed',
            'bowling_style': 'Right-arm off-break',
            'nationality': 'Indian'
        }
    ]

    # Filter players based on search term
    filtered_players = [
        player for player in mock_players 
        if player_name.lower() in player['player_name'].lower()
    ]

    return filtered_players if filtered_players else None

def get_series_matches(series_id: str) -> Optional[Dict]:
    """Fetch matches for a specific series"""
    data = make_api_request(f"series/v1/{series_id}")
    if not data:
        return None

    try:
        series_data = {
            'series_id': series_id,
            'series_name': data.get('seriesName', 'N/A'),
            'matches': data.get('matchDetails', []),
            'series_info': data.get('seriesInfo', {})
        }

        return series_data

    except Exception as e:
        logger.error(f"Error processing series {series_id}: {e}")
        return None

def format_match_for_display(match: Dict) -> Dict:
    """Format match data for consistent display"""
    return {
        'display_name': f"{match.get('team1', 'Team 1')} vs {match.get('team2', 'Team 2')} - {match.get('match_date', 'N/A')} ({match.get('status', 'N/A')})",
        'match_id': match.get('match_id'),
        'team1': match.get('team1', 'Team 1'),
        'team2': match.get('team2', 'Team 2'),
        'series_name': match.get('series_name', 'N/A'),
        'match_date': match.get('match_date', 'N/A'),
        'match_format': match.get('match_format', 'N/A'),
        'venue': match.get('venue', 'N/A'),
        'city': match.get('city', 'N/A'),
        'status': match.get('status', 'N/A')
    }

def get_all_matches():
    """Fetch and combine live, recent, and upcoming matches"""
    all_matches = []

    # Get live matches
    live_matches = get_live_matches()
    if live_matches:
        for match in live_matches:
            match['match_type'] = 'Live'
            all_matches.append(match)

    # Get recent matches
    recent_matches = get_recent_matches()
    if recent_matches:
        for match in recent_matches:
            match['match_type'] = 'Recent'
            all_matches.append(match)

    # Get upcoming matches
    upcoming_matches = get_upcoming_matches()
    if upcoming_matches:
        for match in upcoming_matches:
            match['match_type'] = 'Upcoming'
            all_matches.append(match)

    return all_matches
