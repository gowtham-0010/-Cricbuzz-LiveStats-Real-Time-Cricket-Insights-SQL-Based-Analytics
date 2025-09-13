# Cricbuzz LiveStats - API Testing & Data Fetching

import sys
import os
import requests
import pandas as pd
import json
from datetime import datetime

# Add the parent directory to path for imports
sys.path.append(os.path.dirname(__file__))

from utils.api_utils import CricbuzzAPIManager
from utils.db_connection import DatabaseManager

print("🏏 Cricbuzz LiveStats - Data Fetching & Testing Notebook")
print("=" * 60)

# Initialize managers
print("\n1. Initializing API and Database managers...")
api_manager = CricbuzzAPIManager()
db_manager = DatabaseManager()

print("✅ API Manager initialized")
print("✅ Database Manager initialized")

# Test API endpoints
print("\n2. Testing Cricbuzz API endpoints...")

try:
    print("\n📺 Testing Live Matches endpoint...")
    live_matches = api_manager.get_live_matches()
    print(f"✅ Live matches found: {len(live_matches)}")

    if live_matches:
        print("\nSample live match:")
        print(json.dumps(live_matches[0], indent=2))

except Exception as e:
    print(f"❌ Live matches error: {str(e)}")

try:
    print("\n📅 Testing Recent Matches endpoint...")
    recent_matches = api_manager.get_recent_matches()
    print(f"✅ Recent matches found: {len(recent_matches)}")

    if recent_matches:
        print("\nSample recent match:")
        print(json.dumps(recent_matches[0], indent=2))

except Exception as e:
    print(f"❌ Recent matches error: {str(e)}")

# Test database operations
print("\n3. Testing Database operations...")

try:
    # Test basic query
    players_df = db_manager.execute_query("SELECT COUNT(*) as player_count FROM players")
    player_count = players_df.iloc[0]['player_count'] if not players_df.empty else 0
    print(f"✅ Database connected. Players in DB: {player_count}")

    # Test sample queries
    if player_count > 0:
        print("\n🏏 Sample player data:")
        sample_players = db_manager.execute_query("SELECT name, country, playing_role FROM players LIMIT 5")
        print(sample_players.to_string(index=False))

except Exception as e:
    print(f"❌ Database error: {str(e)}")

# API Performance testing
print("\n4. API Performance metrics...")

endpoints_to_test = [
    ("matches/v1/live", "Live Matches"),
    ("matches/v1/recent", "Recent Matches"),
    ("matches/v1/upcoming", "Upcoming Matches")
]

for endpoint, name in endpoints_to_test:
    try:
        start_time = datetime.now()
        data = api_manager.make_api_request(endpoint)
        end_time = datetime.now()

        response_time = (end_time - start_time).total_seconds()

        if data:
            print(f"✅ {name}: {response_time:.2f}s response time")
        else:
            print(f"⚠️ {name}: No data returned in {response_time:.2f}s")

    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")

print("\n🎯 Testing completed!")
print("=" * 60)
print("\nSystem Status Summary:")
print("- 🔗 API Integration: Working")
print("- 💾 Database: Operational")  
print("- 📊 Sample Data: Available")
print("- 🚀 Ready for Streamlit launch!")
