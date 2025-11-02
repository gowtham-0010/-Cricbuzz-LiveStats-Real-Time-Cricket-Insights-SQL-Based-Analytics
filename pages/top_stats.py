"""
Player Stats Page - Previous UI Design + Real Database Data
Best of both worlds: Rich interface with actual data
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import database functions
try:
    from enhanced_player_data_fetcher import search_player, get_player_info
    IMPORT_SUCCESS = True
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    IMPORT_SUCCESS = False

# Configuration
RAPIDAPI_KEY = "8f28ac76efmshbb48e07d1c830fcp1d4ea9jsn3872535caf88"
DB_PATH = "data/cricbuzz.db"

def show():
    """Main display function"""
    st.markdown("**Title:** Cricbuzz Live Match Dashboard - Player Stats")

    if not IMPORT_SUCCESS:
        st.stop()

    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'selected_player' not in st.session_state:
        st.session_state.selected_player = None
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False

    display_player_search_section()

def display_player_search_section():
    """Display search interface"""
    st.markdown("### Search for a Player")

    search_col1, search_col2 = st.columns([4, 1])

    with search_col1:
        player_name = st.text_input(
            "Enter player name:",
            key="player_search_input",
            placeholder="Enter player name",
            help="Type a player name and click the search button"
        )

    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("🔍", key="search_button", help="Search for player")

    if search_clicked:
        if not player_name or not player_name.strip():
            st.warning("⚠️ Please enter a player name to search")
            st.session_state.search_performed = False
            st.session_state.search_results = []
            return

        with st.spinner(f"Searching for '{player_name}'..."):
            # Search database
            search_results = search_player(player_name.strip(), RAPIDAPI_KEY)

            if search_results:
                st.session_state.search_results = search_results
                st.session_state.search_performed = True
                st.session_state.show_profile = False
            else:
                st.session_state.search_results = []
                st.session_state.search_performed = True
                st.session_state.show_profile = False

    if st.session_state.search_performed:
        display_search_results()

def display_search_results():
    """Display search results"""
    if not st.session_state.search_results:
        st.error("❌ No players found in database.")
        st.info("""
        **Search Tips:**
        - Check spelling
        - Try first or last names only
        - Popular players: MS Dhoni, Virat Kohli, Rohit Sharma
        """)
        return

    num_results = len(st.session_state.search_results)
    st.success(f"✅ Player found in database")
    st.info(f"Found {num_results} player(s) matching your search")

    # Create player options
    player_options = {}
    for player in st.session_state.search_results:
        player_name = player.get('name', 'Unknown')
        team_name = player.get('teamName', 'Unknown Team')

        # Try to get DOB from database if available
        player_id = player.get('id')
        dob_display = ""

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT date_of_birth FROM players_real WHERE player_id = ?", (player_id,))
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                dob_display = f" - Born: {result[0]}"
        except:
            pass

        display_text = f"{player_name} ({team_name}){dob_display}"
        player_options[display_text] = player

    st.markdown("---")
    st.markdown("### Select a Player from Results")

    selected_display = st.selectbox(
        "Choose a player:",
        options=list(player_options.keys()),
        key="player_selector",
        help="Select a player to view detailed profile"
    )

    selected_player = player_options[selected_display]

    if st.button(f"📋 Show Profile for {selected_player.get('name')}"):
        st.session_state.selected_player = selected_player
        st.session_state.show_profile = True

    if st.session_state.show_profile and st.session_state.selected_player:
        display_player_profile(st.session_state.selected_player)

def display_player_profile(player):
    """Display comprehensive player profile - REAL DATA FROM DATABASE"""
    player_name = player.get('name', 'Unknown Player')
    player_id = player.get('id')
    team_name = player.get('teamName', 'Unknown Team')

    st.markdown("---")
    st.markdown(f"## {player_name} - Player Profile")

    # Get real data from database
    player_stats = get_player_info(player_id, RAPIDAPI_KEY)

    if player_stats:
        profile = player_stats.get('profile', {})
        nickname = profile.get('nickName', get_player_nickname(player_name))
    else:
        nickname = get_player_nickname(player_name)

    st.markdown(f"**Nickname:** {nickname}")

    # Three tabs like previous version
    tab1, = st.tabs([
        "📋 Tab 1: Profile"
    ])

    with tab1:
        display_profile_tab(player, player_stats)

    # with tab2:
    #     display_batting_stats_tab(player, player_stats)

    # with tab3:
    #     display_bowling_stats_tab(player, player_stats)

def display_profile_tab(player, player_stats):
    """Tab 1: Profile - REAL DATA FROM DATABASE"""
    st.markdown("### Tab 1: Profile")

    col1, col2 = st.columns(2)

    with col1:
        player_name = player.get('name', 'N/A')
        team_name = player.get('teamName', 'N/A')

        # Get real data from database
        if player_stats:
            profile = player_stats.get('profile', {})
            role = profile.get('role', player.get('role', 'N/A'))
            batting_style = profile.get('battingStyle', player.get('battingStyle', 'N/A'))
            bowling_style = profile.get('bowlingStyle', player.get('bowlingStyle', 'N/A'))
            intl_team = profile.get('internationalTeam', team_name)
        else:
            role = player.get('role', 'N/A')
            batting_style = player.get('battingStyle', 'N/A')
            bowling_style = player.get('bowlingStyle', 'N/A')
            intl_team = team_name

        st.markdown(f"""
        **Role in Team:** {role}  
        **Batting Style:** {batting_style}  
        **Bowling Style:** {bowling_style}  
        **International Team:** {intl_team}
        """)

    with col2:
        # Get real personal data from database
        if player_stats:
            profile = player_stats.get('profile', {})
            dob = profile.get('dateOfBirth', 'N/A')
            birth_place = profile.get('birthPlace', 'N/A')
        else:
            dob = 'N/A'
            birth_place = 'N/A'

        age = calculate_age(dob) if dob != 'N/A' else 'N/A'

        st.markdown(f"""
        **DOB:** {dob}  
        **Age:** {age}  
        **Birth Place:** {birth_place}  
        **Height:** N/A  
        **Weight:** N/A
        """)

    # Teams played for - REAL DATA
    st.markdown("#### Teams Played For")

    if player_stats:
        profile = player_stats.get('profile', {})
        teams_played_str = profile.get('teamsPlayed', '')

        if teams_played_str:
            st.markdown(f"**Teams:** {teams_played_str}")
        else:
            st.markdown(f"**Teams:** {team_name}")
    else:
        st.markdown(f"**Teams:** {team_name}")

    # Cricbuzz profile link
    player_id = player.get('id', '0')
    url_name = player.get('name', '').lower().replace(' ', '-').replace('.', '')
    cricbuzz_url = f"https://www.cricbuzz.com/profiles/{player_id}/{url_name}"
    st.markdown(f"#### Full Profile Link\n🔗 [Official Profile]({cricbuzz_url})")

def display_batting_stats_tab(player, player_stats):
    """Tab 2: Batting Stats - Note: Cricbuzz API doesn't provide format-wise stats"""
    st.markdown("### Tab 2: Batting Stats")
    st.markdown("#### Batting Career Statistics")

    # Show message about data availability
    st.info("""
    ℹ️ **Note:** The Cricbuzz API provides player profile information but does not 
    include detailed format-wise batting statistics (Test, ODI, T20I breakdowns).

    For complete batting statistics, please visit the player's official Cricbuzz profile 
    using the link in Tab 1.
    """)

    # Show what we DO have from database
    if player_stats:
        profile = player_stats.get('profile', {})

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Available Information:**")
            st.markdown(f"- **Batting Style:** {profile.get('battingStyle', 'N/A')}")
            st.markdown(f"- **Role:** {profile.get('role', 'N/A')}")

        with col2:
            st.markdown("**Career Highlights:**")
            st.markdown("- Full statistics available on Cricbuzz profile")
            st.markdown("- Real-time match performance in live matches")
    else:
        st.warning("⚠️ Detailed statistics not available in database")

def display_bowling_stats_tab(player, player_stats):
    """Tab 3: Bowling Stats"""
    st.markdown("### Tab 3: Bowling Stats")
    st.markdown("#### Career Bowling Statistics")

    # Check if player is a bowler
    if player_stats:
        profile = player_stats.get('profile', {})
        bowling_style = profile.get('bowlingStyle', '')
        role = profile.get('role', '').lower()

        if bowling_style and bowling_style != 'N/A':
            st.info(f"""
            ℹ️ **Note:** The Cricbuzz API provides player profile information but does not 
            include detailed bowling statistics breakdowns.

            **Bowling Style:** {bowling_style}
            **Role:** {profile.get('role', 'N/A')}

            For complete bowling statistics, please visit the official Cricbuzz profile.
            """)
        else:
            st.info("This player is primarily a batsman with no bowling statistics.")
    else:
        st.warning("⚠️ Bowling statistics not available")

def get_player_nickname(player_name: str) -> str:
    """Get player nickname - fallback if not in database"""
    name_lower = player_name.lower()

    # Well-known nicknames
    nicknames = {
        'dhoni': 'Captain Cool',
        'kohli': 'King Kohli',
        'rohit': 'Hitman',
        'gayle': 'Universe Boss',
        'bumrah': 'Boom Boom',
        'jadeja': 'Sir Jadeja',
        'ashwin': 'Ash',
        'smith': 'Smudge',
        'warner': 'Bull',
        'williamson': 'Kane Train'
    }

    for key, nickname in nicknames.items():
        if key in name_lower:
            return nickname

    return "Cricket Star"

def calculate_age(dob_string: str) -> str:
    """Calculate age from DOB string"""
    try:
        # Handle different date formats
        for fmt in ["%B %d, %Y", "%Y-%m-%d", "%d-%m-%Y"]:
            try:
                # Remove any extra text like "(XX years)"
                dob_clean = dob_string.split('(')[0].strip()
                dob = datetime.strptime(dob_clean, fmt)
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return f"{age} years"
            except:
                continue
        return "N/A"
    except:
        return "N/A"

if __name__ == "__main__":
    show()
