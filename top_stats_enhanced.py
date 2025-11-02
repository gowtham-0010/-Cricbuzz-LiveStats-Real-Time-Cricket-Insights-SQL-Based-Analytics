"""
Player Stats Page - Uses Database for Player Search
Displays real data from stored players in database
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from enhanced_player_data_fetcher import CricbuzzPlayerAPI, search_player, get_player_info, initialize_database
except ImportError:
    st.error("❌ Error: enhanced_player_data_fetcher.py not found")
    st.stop()

# API Configuration
RAPIDAPI_KEY = "8f28ac76efmshbb48e07d1c830fcp1d4ea9jsn3872535caf88"
DB_PATH = "data/cricbuzz.db"

def show():
    """Main function to display the player stats page"""
    st.markdown("### 🏏 Cricbuzz Live Match Dashboard - Player Stats")
    st.info("📊 Displaying REAL DATA from Database - Fetched from Cricbuzz API")

    # Check database status
    check_database_status()

    # Display player search section
    display_player_search_section()

def check_database_status():
    """Check if player database exists and show status"""
    if not os.path.exists(DB_PATH):
        st.warning("⚠️ Player database not found.")
        st.info("💡 Run: `python initialize_data.py` to build the database")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM players_real")
        total_players = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM players_real WHERE has_detailed_stats = 1")
        players_with_stats = cursor.fetchone()[0]

        conn.close()

        if total_players == 0:
            st.warning("⚠️ Database is empty")
            st.info("💡 Run: `python initialize_data.py` to fetch players")
            return

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Players", total_players)
        with col2:
            st.metric("✅ With Detailed Stats", players_with_stats)
        with col3:
            st.metric("ℹ️ Basic Info Only", total_players - players_with_stats)
    except Exception as e:
        st.error(f"❌ Database error: {e}")

def display_player_search_section():
    """Display the player search interface"""
    st.markdown("---")
    st.markdown("### 🔍 Search for a Player")

    # Search input
    search_col1, search_col2 = st.columns([4, 1])

    with search_col1:
        player_name = st.text_input(
            "Enter player name",
            key="player_search_input",
            placeholder="e.g., Virat Kohli, MS Dhoni, Steve Smith...",
            help="Search for international cricket players"
        )

    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search", key="search_button")

    # Handle search
    if search_clicked:
        if not player_name or not player_name.strip():
            st.warning("⚠️ Please enter a player name to search")
            return

        with st.spinner(f"🔍 Searching for '{player_name}'..."):
            search_results = search_player(player_name.strip(), RAPIDAPI_KEY)

            if not search_results:
                st.error("❌ No players found in database")
                st.info("💡 Try: Virat Kohli, MS Dhoni, Rohit Sharma, Steve Smith")
                return

            display_search_results(search_results)

def display_search_results(search_results):
    """Display search results"""
    num_results = len(search_results)
    st.success(f"✅ Found {num_results} player(s)")

    # Create player options
    player_options = {}
    for player in search_results:
        player_name = player.get("name", "Unknown")
        team_name = player.get("teamName", "Unknown Team")
        role = player.get("role", "Unknown")
        has_stats = "📊 Detailed" if player.get("hasDetailedStats") else "ℹ️ Basic"

        display_text = f"{player_name} ({team_name}) - {role} - {has_stats}"
        player_options[display_text] = player

    st.markdown("---")
    st.markdown("### 📋 Select a Player")

    selected_display = st.selectbox(
        "Choose a player to view profile:",
        options=list(player_options.keys()),
        key="player_selector"
    )

    selected_player = player_options[selected_display]

    if st.button(f"👤 Show Profile for {selected_player.get('name')}", key="show_profile_btn"):
        display_player_profile(selected_player)

def display_player_profile(player):
    """Display comprehensive player profile"""
    player_name = player.get("name", "Unknown Player")
    player_id = player.get("id", "")
    has_detailed_stats = player.get("hasDetailedStats", False)

    st.markdown("---")
    st.markdown(f"## 🏏 {player_name} - Player Profile")

    if not has_detailed_stats:
        st.warning("ℹ️ This player has basic information only")
    else:
        st.success("✅ Detailed statistics available")

    # Get stats from database
    player_stats = get_player_info(player_id, RAPIDAPI_KEY)

    if not player_stats:
        st.error("❌ Could not load player statistics")
        return

    # Create tabs
    tab1, tab2 = st.tabs(["📝 Profile", "📊 Biography"])

    with tab1:
        display_profile_tab(player, player_stats)

    with tab2:
        display_bio_tab(player_stats)

def display_profile_tab(player, player_stats):
    """Display player profile information"""
    st.markdown("### 📝 Player Profile")

    profile = player_stats.get("profile", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏏 Cricket Information")

        role = profile.get("role") or player.get("role", "Unknown")
        batting_style = profile.get("battingStyle") or player.get("battingStyle", "Not specified")
        bowling_style = profile.get("bowlingStyle") or player.get("bowlingStyle", "Not specified")
        intl_team = profile.get("internationalTeam") or player.get("nationality", "Unknown")

        st.markdown(f"**Role:** {role}")
        st.markdown(f"**Batting Style:** {batting_style}")
        st.markdown(f"**Bowling Style:** {bowling_style}")
        st.markdown(f"**International Team:** {intl_team}")

    with col2:
        st.markdown("#### 👤 Personal Information")

        dob = profile.get("dateOfBirth", "Not available")
        birthplace = profile.get("birthPlace", "Not available")
        nick_name = profile.get("nickName", player.get("nickName", ""))

        if nick_name:
            st.markdown(f"**Nickname:** {nick_name}")
        st.markdown(f"**Date of Birth:** {dob}")
        st.markdown(f"**Birth Place:** {birthplace}")

    # Teams played for
    st.markdown("#### 🏆 Teams Played For")
    teams_played = profile.get("teamsPlayed", "")
    if teams_played:
        st.markdown(f"**Teams:** {teams_played}")
    else:
        st.markdown(f"**Teams:** {player.get('teamName', 'Unknown')}")

    # Cricbuzz profile link
    player_id = player.get("id", "0")
    url_name = player.get("name", "").lower().replace(" ", "-").replace(".", "")
    cricbuzz_url = f"https://www.cricbuzz.com/profiles/{player_id}/{url_name}"
    st.markdown(f"🔗 [**View Full Profile on Cricbuzz**]({cricbuzz_url})")

def display_bio_tab(player_stats):
    """Display player biography"""
    st.markdown("### 📖 Player Biography")

    profile = player_stats.get("profile", {})
    bio = profile.get("bio", "")

    if bio:
        # Clean up HTML tags if present
        bio_clean = bio.replace("<br/>", "\n\n").replace("<b>", "**").replace("</b>", "**")
        st.markdown(bio_clean)
    else:
        st.info("ℹ️ Biography not available for this player")

if __name__ == "__main__":
    show()
