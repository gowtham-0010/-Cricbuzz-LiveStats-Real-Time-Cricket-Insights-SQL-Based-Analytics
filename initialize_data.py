"""
Incremental Player Data Sync - NO PROMPTS
Automatically adds more players each run - safe to stop anytime
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

try:
    from enhanced_player_data_fetcher import CricbuzzPlayerAPI, initialize_database
except ImportError:
    print("❌ Error: enhanced_player_data_fetcher.py not found!")
    print("   Make sure it's in the same directory")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = "d9ce22edb5msh7f4ea8ba68cf789p19cd33jsn543e73adfde7"
DB_PATH = "data/cricbuzz.db"

def get_db_stats():
    """Get current database statistics"""
    if not os.path.exists(DB_PATH):
        return {"exists": False, "total": 0, "detailed": 0}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM players_real")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM players_real WHERE has_detailed_stats = 1")
        detailed = cursor.fetchone()[0]

        conn.close()

        return {"exists": True, "total": total, "detailed": detailed}
    except:
        return {"exists": True, "total": 0, "detailed": 0}

def main():
    """Main sync function - NO PROMPTS"""

    print("=" * 70)
    print("🏏 CRICBUZZ LIVESTATS - INCREMENTAL PLAYER SYNC")
    print("=" * 70)
    print()

    # Show current status
    before_stats = get_db_stats()

    if before_stats["exists"]:
        print("📊 Current Database Status:")
        print(f"   Total players: {before_stats['total']}")
        print(f"   With detailed stats: {before_stats['detailed']}")
        print(f"   Basic info only: {before_stats['total'] - before_stats['detailed']}")
    else:
        print("📊 Status: New database will be created")

    print()
    print("🔄 Mode: INCREMENTAL UPDATE")
    print("   ✅ Skips already fetched players")
    print("   ✅ Adds new players from API")
    print("   ✅ No duplicates (INSERT OR REPLACE)")
    print("   ✅ Commits after each player")
    print("   ✅ Safe to stop anytime (Ctrl+C)")
    print()

    # Start sync
    start_time = datetime.now()
    print(f"🚀 Starting sync at {start_time.strftime('%H:%M:%S')}")
    print("=" * 70)
    print()

    try:
        # Run incremental update
        added = initialize_database(API_KEY, DB_PATH)

        # Get final stats
        after_stats = get_db_stats()

        # Calculate time
        end_time = datetime.now()
        elapsed = end_time - start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)

        print()
        print("=" * 70)
        print("🎉 SYNC COMPLETED!")
        print("=" * 70)
        print()
        print("📊 Final Statistics:")
        print(f"   Total players: {after_stats['total']}")
        print(f"   With detailed stats: {after_stats['detailed']}")
        print(f"   Basic info only: {after_stats['total'] - after_stats['detailed']}")
        print()
        print(f"📈 This Run:")
        print(f"   Players added: {after_stats['total'] - before_stats['total']}")
        print(f"   Detailed stats added: {after_stats['detailed'] - before_stats['detailed']}")
        print()
        print(f"⏱️  Time taken: {minutes}m {seconds}s")
        print()
        print("💡 Tip: Run again to fetch more players!")
        print("=" * 70)

    except KeyboardInterrupt:
        print()
        print()
        print("=" * 70)
        print("⏹️  STOPPED BY USER")
        print("=" * 70)
        print()

        after_stats = get_db_stats()
        print("📊 Progress saved:")
        print(f"   Total players: {after_stats['total']}")
        print(f"   With detailed stats: {after_stats['detailed']}")
        print(f"   Added this run: {after_stats['total'] - before_stats['total']}")
        print()
        print("✅ All data is saved!")
        print("🔄 Run again to continue from where you left off")
        print("=" * 70)

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR OCCURRED")
        print("=" * 70)
        print(f"   {str(e)}")
        print()
        print("🔍 Troubleshooting:")
        print("   - Check internet connection")
        print("   - Verify API key is correct")
        print("   - Check database file permissions")
        logger.exception("Full error details:")

if __name__ == "__main__":
    main()
