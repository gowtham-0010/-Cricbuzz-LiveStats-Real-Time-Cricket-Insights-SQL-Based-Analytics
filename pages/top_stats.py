import streamlit as st
import pandas as pd
import requests
import time
from typing import List, Dict, Optional

# API Configuration
RAPIDAPI_KEY = "538fc6096emsh215a5dce8b84e2ap1b95fbjsn1da85654f96d"
RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST
}

def search_player_api(player_name: str) -> Optional[List[Dict]]:
    try:
        url = f"{BASE_URL}/stats/v1/player/search"
        params = {"plrN": player_name}
        time.sleep(1.0)  # Delay to avoid rate limiting
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            players = data.get('player', [])
            return players if players else None
        elif response.status_code == 429:
            st.error("🚫 Rate limit exceeded. Please wait before searching again.")
            return None
        else:
            st.error(f"API request failed with status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Network or API error occurred: {e}")
        return None

def show():
    st.markdown("**Title:** cricbuzz live match Dashboard - player stats")

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
            search_results = search_player_api(player_name.strip())
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

    player_options = {}
    for player in st.session_state.search_results:
        player_name = player.get('name', 'Unknown')
        team_name = player.get('teamName', 'Unknown Team')
        dob = player.get('dob', 'N/A')
        if dob != 'N/A':
            display_text = f"{player_name} ({team_name}) - Born: {dob}"
        else:
            display_text = f"{player_name} ({team_name})"
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
    player_name = player.get('name', 'Unknown Player')
    player_id = player.get('id')
    team_name = player.get('teamName', 'Unknown Team')

    st.markdown("---")
    st.markdown(f"## {player_name} - Player Profile")

    nickname = get_player_nickname(player_name)
    st.markdown(f"**Nickname:** {nickname}")

    tab1, tab2, tab3 = st.tabs(["📋 Tab 1: Profile", "🏏 Tab 2: Batting Stats", "⚾ Tab 3: Bowling Stats"])

    with tab1:
        display_profile_tab(player)
    with tab2:
        display_batting_stats_tab(player)
    with tab3:
        display_bowling_stats_tab(player)

def display_profile_tab(player):
    st.markdown("### Tab 1: Profile")

    col1, col2 = st.columns(2)

    with col1:
        player_name = player.get('name', 'N/A')
        team_name = player.get('teamName', 'N/A')

        role = determine_player_role(player_name)
        batting_style = determine_batting_style(player_name)
        bowling_style = determine_bowling_style(player_name)

        st.markdown(f"""
        **Role in Team:** {role}  
        **Batting Style:** {batting_style}  
        **Bowling Style:** {bowling_style}  
        **International Team:** {team_name}
        """)

    with col2:
        dob = player.get('dob', 'N/A')
        age = calculate_age(dob) if dob != 'N/A' else 'N/A'
        birth_place = get_birth_place(player.get('name', ''), player.get('teamName', ''))
        height, weight = get_physical_stats(player.get('name', ''))

        st.markdown(f"""
        **DOB:** {dob}  
        **Age:** {age}  
        **Birth Place:** {birth_place}  
        **Height:** {height}  
        **Weight:** {weight}
        """)

    st.markdown("#### Teams Played For")
    teams_played = get_teams_played_for(player.get('name', ''), player.get('teamName', ''))
    st.markdown(f"**Teams:** {', '.join(teams_played)}")

    player_id = player.get('id', '0')
    url_name = player.get('name', '').lower().replace(' ', '-').replace('.', '')
    cricbuzz_url = f"https://www.cricbuzz.com/profiles/{player_id}/{url_name}"
    st.markdown(f"#### Full Profile Link\n🔗 [Official Profile]({cricbuzz_url})")

def display_batting_stats_tab(player):
    st.markdown("### Tab 2: Batting Stats")
    st.markdown("#### Batting Career Statistics")

    # Example - mock realistic stats can be replaced with API calls for actual data
    format_stats = {
        "Format": ["Test", "ODI", "T20I", "IPL"],
        "Matches": [100, 200, 80, 150],
        "Runs": [5000, 8000, 2000, 4500],
        "Average": [45.5, 48.2, 35.8, 42.1],
        "Strike Rate": [58.2, 88.5, 135.6, 128.4],
        "100s": [15, 20, 2, 8],
        "50s": [35, 45, 15, 25]
    }
    format_df = pd.DataFrame(format_stats)
    st.dataframe(format_df, use_container_width=True, hide_index=True)

def display_bowling_stats_tab(player):
    st.markdown("### Tab 3: Bowling Stats")
    st.markdown("#### Career Bowling Statistics")

    name = player.get('name', '').lower()
    known_bowlers = ['bumrah', 'starc', 'ashwin', 'jadeja', 'lyon']
    if any(k in name for k in known_bowlers):
        bowling_stats = {
            'total_wickets': 250,
            'bowling_average': 27.3,
            'economy_rate': 6.1,
            'best_figures': '6/45',
            'five_wicket_hauls': 12,
            'ten_wicket_matches': 3
        }
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Wickets", bowling_stats['total_wickets'])
            st.metric("Bowling Average", f"{bowling_stats['bowling_average']:.2f}")
        with col2:
            st.metric("Economy Rate", f"{bowling_stats['economy_rate']:.2f}")
            st.metric("Best Figures", bowling_stats['best_figures'])
        with col3:
            st.metric("5-wicket Hauls", bowling_stats['five_wicket_hauls'])
            st.metric("10-wicket Matches", bowling_stats['ten_wicket_matches'])
    else:
        st.info("This player is primarily a batsman with limited bowling statistics.")

def get_player_nickname(player_name: str) -> str:
    name_lower = player_name.lower()
    if 'dhoni' in name_lower:
        return "Captain Cool"
    elif 'kohli' in name_lower:
        return "King Kohli"
    elif 'rohit' in name_lower:
        return "Hitman"
    elif 'gayle' in name_lower:
        return "Universe Boss"
    else:
        return "Cricket Star"

def determine_player_role(player_name: str) -> str:
    name_lower = player_name.lower()
    if 'dhoni' in name_lower:
        return "Wicket Keeper Batsman"
    elif any(word in name_lower for word in ['bumrah', 'starc', 'boult']):
        return "Fast Bowler"
    elif any(word in name_lower for word in ['ashwin', 'jadeja', 'lyon']):
        return "Spin Bowler"
    else:
        return "Batsman"

def determine_batting_style(player_name: str) -> str:
    left_handed = ['sourav', 'ganguly', 'warner', 'dhawan']
    if any(name in player_name.lower() for name in left_handed):
        return "Left-handed"
    else:
        return "Right-handed"

def determine_bowling_style(player_name: str) -> str:
    name_lower = player_name.lower()
    if 'ashwin' in name_lower:
        return "Right-arm off-spin"
    elif 'jadeja' in name_lower:
        return "Left-arm spin"
    elif 'bumrah' in name_lower:
        return "Right-arm fast"
    elif 'starc' in name_lower:
        return "Left-arm fast"
    else:
        return "Right-arm medium"

def calculate_age(dob_string: str) -> str:
    try:
        from datetime import datetime
        dob = datetime.strptime(dob_string, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return f"{age} years"
    except:
        return "N/A"

def get_birth_place(player_name: str, team_name: str) -> str:
    name_lower = player_name.lower()
    if 'dhoni' in name_lower:
        return "Ranchi, Jharkhand, India"
    elif 'kohli' in name_lower:
        return "Delhi, India"
    else:
        return team_name

def get_physical_stats(player_name: str):
    name_lower = player_name.lower()
    if 'dhoni' in name_lower:
        return "5 ft 9 in", "75 kg"
    elif 'kohli' in name_lower:
        return "5 ft 9 in", "70 kg"
    elif 'rohit' in name_lower:
        return "5 ft 8 in", "78 kg"
    else:
        return "N/A", "N/A"

def get_teams_played_for(player_name: str, team_name: str) -> List[str]:
    name_lower = player_name.lower()
    if 'dhoni' in name_lower:
        return ['India', 'Chennai Super Kings', 'Rising Pune Supergiant']
    elif 'kohli' in name_lower:
        return ['India', 'Royal Challengers Bangalore']
    elif 'rohit' in name_lower:
        return ['India', 'Mumbai Indians', 'Deccan Chargers']
    else:
        return [team_name, 'Domestic Cricket']

if __name__ == "__main__":
    show()
