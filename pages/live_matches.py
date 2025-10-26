"""
Live Matches Page - FINAL WORKING VERSION
Handles both timestamp and pre-formatted dates correctly
"""

import streamlit as st
import pandas as pd
from utils.api_utils import get_all_matches, get_match_scorecard
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_timestamp_to_date(timestamp_value):
    """
    Convert timestamp to readable date - handles both milliseconds and strings
    """
    try:
        # If already a string (pre-formatted), return it
        if isinstance(timestamp_value, str):
            # If it looks like a timestamp string, convert it
            if timestamp_value.isdigit():
                timestamp_ms = int(timestamp_value)
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                return dt.strftime("%d %b %Y")
            # Otherwise return as-is
            return timestamp_value
        
        # If numeric (int or float)
        if isinstance(timestamp_value, (int, float)) and timestamp_value > 0:
            dt = datetime.fromtimestamp(timestamp_value / 1000)
            return dt.strftime("%d %b %Y")
        
        return "TBD"
    except Exception as e:
        logger.error(f"Date conversion error: {e} for value: {timestamp_value}")
        return str(timestamp_value) if timestamp_value else "TBD"

def show():
    """Display the Live Scores page"""
    
    # Initialize session state
    if 'selected_match_index' not in st.session_state:
        st.session_state.selected_match_index = 0
    if 'show_scorecard' not in st.session_state:
        st.session_state.show_scorecard = False
    if 'last_selected_match' not in st.session_state:
        st.session_state.last_selected_match = None

    # Fetch all matches
    with st.spinner("Fetching match data..."):
        all_matches = get_all_matches()

    if not all_matches:
        st.error("❌ Unable to fetch match data from API")
        return

    st.success(f"✅ Found {len(all_matches)} matches")

    # Match selection
    st.markdown("### Select a Match")

    # Create display options with date conversion
    match_display_options = []
    for i, match in enumerate(all_matches):
        team1 = match.get('team1', 'Team 1')
        team2 = match.get('team2', 'Team 2')
        
        # Convert date (handles all formats)
        raw_date = match.get('match_date', 'TBD')
        match_date = convert_timestamp_to_date(raw_date)
        
        match_type = match.get('match_type', 'Match')
        
        display_text = f"{team1} vs {team2} - {match_date} ({match_type})"
        match_display_options.append(display_text)

    if not match_display_options:
        st.error("❌ No matches available")
        return

    # Ensure index is valid
    if st.session_state.selected_match_index >= len(all_matches):
        st.session_state.selected_match_index = 0

    # Callback for match selection
    def on_match_change():
        """Callback when match selection changes"""
        st.session_state.show_scorecard = False
        st.session_state.last_selected_match = st.session_state.match_selector

    # Match selector
    selected_index = st.selectbox(
        "Choose a match:",
        options=list(range(len(match_display_options))),
        format_func=lambda x: match_display_options[x],
        index=st.session_state.selected_match_index,
        key="match_selector",
        on_change=on_match_change
    )

    # Update session state
    if selected_index != st.session_state.selected_match_index:
        st.session_state.selected_match_index = selected_index
        st.session_state.show_scorecard = False
        st.rerun()

    # Get selected match
    current_selected_index = st.session_state.get('match_selector', selected_index)
    selected_match = all_matches[current_selected_index]

    # Display selection
    st.markdown(f"**Currently viewing:** {match_display_options[current_selected_index]}")
    
    # Display sections
    display_match_details(selected_match)
    display_current_score_details(selected_match)  
    display_scorecard_section(selected_match, current_selected_index)

def display_match_details(match):
    """Display match details"""
    
    st.markdown("### Match Information")
    
    # Get match data
    team1 = match.get('team1', 'N/A')
    team2 = match.get('team2', 'N/A')
    series_name = match.get('series_name', 'N/A')
    
    # Convert date
    raw_date = match.get('match_date', 'N/A')
    match_date = convert_timestamp_to_date(raw_date)
    
    match_format = match.get('match_format', 'N/A')
    venue = match.get('venue', 'N/A')
    city = match.get('city', 'N/A')
    status = match.get('status', 'N/A')
    match_type = match.get('match_type', 'N/A')
    match_id = match.get('match_id', 'N/A')

    # Gradient card
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%); 
                padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0;">
        <h2 style="color: white; margin: 0;">{team1} vs {team2}</h2>
        <p style="color: white; margin: 0; font-size: 0.9em;">Match ID: {match_id}</p>
    </div>
    """, unsafe_allow_html=True)

    # Match details
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Series:** {series_name}")
        st.markdown(f"**Date:** {match_date}")
        st.markdown(f"**Format:** {match_format}")

    with col2:
        st.markdown(f"**Venue:** {venue}")
        st.markdown(f"**City:** {city}")
        st.markdown(f"**Status:** {status}")

    with col3:
        st.markdown(f"**Type:** {match_type}")
        st.markdown(f"**Updated:** {datetime.now().strftime('%H:%M:%S')}")

def display_current_score_details(match):
    """Display current scores"""
    
    st.markdown("### Current Scores")
    
    team1 = match.get('team1', 'Team 1')
    team2 = match.get('team2', 'Team 2')
    status = match.get('status', 'N/A')

    team1_short = get_team_short_name(team1)
    team2_short = get_team_short_name(team2)

    match_score = match.get('match_score', {})

    if match_score:
        team1_score_data = match_score.get('team1Score', {})
        team2_score_data = match_score.get('team2Score', {})

        team1_inngs1 = team1_score_data.get('inngs1', {})
        team1_inngs2 = team1_score_data.get('inngs2', {})
        team2_inngs1 = team2_score_data.get('inngs1', {})
        team2_inngs2 = team2_score_data.get('inngs2', {})

        score_lines = []

        # Team 1 scores
        if team1_inngs1:
            runs = team1_inngs1.get('runs', 0)
            wickets = team1_inngs1.get('wickets', 0)
            overs = team1_inngs1.get('overs', 0.0)
            score_lines.append(f"**{team1_short}** Innings 1: {runs}/{wickets} ({overs} overs)")

        if team1_inngs2:
            runs = team1_inngs2.get('runs', 0)
            wickets = team1_inngs2.get('wickets', 0)
            overs = team1_inngs2.get('overs', 0.0)
            score_lines.append(f"**{team1_short}** Innings 2: {runs}/{wickets} ({overs} overs)")

        # Team 2 scores
        if team2_inngs1:
            runs = team2_inngs1.get('runs', 0)
            wickets = team2_inngs1.get('wickets', 0)
            overs = team2_inngs1.get('overs', 0.0)
            score_lines.append(f"**{team2_short}** Innings 1: {runs}/{wickets} ({overs} overs)")

        if team2_inngs2:
            runs = team2_inngs2.get('runs', 0)
            wickets = team2_inngs2.get('wickets', 0)
            overs = team2_inngs2.get('overs', 0.0)
            score_lines.append(f"**{team2_short}** Innings 2: {runs}/{wickets} ({overs} overs)")

        if score_lines:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
                <h4 style="margin-top: 0; text-align: center;">🏏 Live Scores</h4>
            </div>
            """, unsafe_allow_html=True)

            for score_line in score_lines:
                st.markdown(f"• {score_line}")

            st.success(f"**Result:** {status}")
        else:
            st.info(f"**{team1_short} vs {team2_short}** - {status}")
    else:
        st.info(f"**{team1_short} vs {team2_short}** - {status}")

def get_team_short_name(team_name):
    """Generate team short name"""
    if not team_name or team_name == 'N/A':
        return 'TBD'

    team_shorts = {
        'India': 'IND', 'Australia': 'AUS', 'England': 'ENG', 'South Africa': 'SA',
        'New Zealand': 'NZ', 'Pakistan': 'PAK', 'Bangladesh': 'BAN', 'Sri Lanka': 'SL',
        'Afghanistan': 'AFG', 'West Indies': 'WI', 'Hong Kong': 'HK',
        'United Arab Emirates': 'UAE', 'Netherlands': 'NED', 'Ireland': 'IRE',
        'Chennai Super Kings': 'CSK', 'Mumbai Indians': 'MI', 
        'Royal Challengers Bangalore': 'RCB', 'Kolkata Knight Riders': 'KKR',
        'Delhi Capitals': 'DC', 'Punjab Kings': 'PBKS', 'Rajasthan Royals': 'RR',
        'Sunrisers Hyderabad': 'SRH', 'Gujarat Titans': 'GT', 'Lucknow Super Giants': 'LSG'
    }

    if team_name in team_shorts:
        return team_shorts[team_name]

    for full_name, short_name in team_shorts.items():
        if full_name.lower() in team_name.lower():
            return short_name

    words = team_name.split()
    if len(words) >= 2:
        return ''.join([word[0].upper() for word in words[:3]])
    return team_name[:3].upper()

def display_scorecard_section(match, match_index):
    """Display scorecard section"""
    
    st.markdown("### Detailed Scorecard")
    
    team1 = match.get('team1', 'Team 1')
    team2 = match.get('team2', 'Team 2')
    match_id = match.get('match_id')

    load_button_key = f"load_btn_{match_id}_{match_index}"
    hide_button_key = f"hide_btn_{match_id}_{match_index}"

    if st.button("🏏 Load Scorecard", key=load_button_key):
        st.session_state.show_scorecard = True
        st.rerun()

    if st.session_state.show_scorecard:
        if not match_id:
            st.error("❌ Match ID not available")
        else:
            with st.spinner(f"Loading scorecard for {team1} vs {team2}..."):
                scorecard_data = get_match_scorecard(str(match_id))

            if scorecard_data:
                st.success(f"✅ Scorecard loaded for {team1} vs {team2}")
                display_scorecard_tables(scorecard_data, team1, team2)
            else:
                st.warning("⚠️ Scorecard not available for this match")
                display_basic_match_info(match, team1, team2)

        if st.button("❌ Hide Scorecard", key=hide_button_key):
            st.session_state.show_scorecard = False
            st.rerun()

def display_scorecard_tables(scorecard_data, team1, team2):
    """Display scorecard tables"""
    
    st.markdown("#### 📊 Complete Scorecard")
    
    try:
        innings = scorecard_data.get('innings', [])
        
        if not innings:
            st.warning("⚠️ No innings data available")
            st.info(f"Match Status: {scorecard_data.get('status', 'N/A')}")
            return
        
        st.success(f"✅ Found {len(innings)} innings")
        
        tabs = st.tabs([f"Innings {i+1}" for i in range(len(innings))])
        
        for i, (tab, inning) in enumerate(zip(tabs, innings)):
            with tab:
                display_single_innings(inning, i+1)
        
        if 'status' in scorecard_data:
            st.markdown("---")
            st.info(f"**Match Status:** {scorecard_data['status']}")
                
    except Exception as e:
        st.error(f"❌ Error displaying scorecard: {e}")
        logger.error(f"Scorecard error: {e}")
        with st.expander("🔍 Debug - Raw Data"):
            st.json(scorecard_data)

def display_single_innings(innings_data, innings_num):
    """Display single innings"""
    
    team_name = innings_data.get('batteamname', f'Team {innings_num}')
    st.markdown(f"### 🏏 {team_name} Innings")
    
    score = innings_data.get('score', 0)
    wickets = innings_data.get('wickets', 0)
    overs = innings_data.get('overs', 0)
    st.markdown(f"**Total:** {score}/{wickets} ({overs} overs)")
    
    # Batting
    st.markdown("#### Batting")
    batsmen = innings_data.get('batsman', [])
    
    if batsmen:
        batting_rows = []
        for player in batsmen:
            if player.get('balls', 0) > 0 or player.get('runs', 0) > 0:
                batting_rows.append({
                    'Batsman': player.get('name', 'Unknown'),
                    'Runs': player.get('runs', 0),
                    'Balls': player.get('balls', 0),
                    '4s': player.get('fours', 0),
                    '6s': player.get('sixes', 0),
                    'SR': player.get('strkrate', '0'),
                    'Dismissal': player.get('outdec', 'not out')
                })
        
        if batting_rows:
            batting_df = pd.DataFrame(batting_rows)
            st.dataframe(batting_df, use_container_width=True, hide_index=True)
        else:
            st.info("No batting data")
    else:
        st.info("No batting data available")
    
    # Bowling
    st.markdown("#### Bowling")
    bowlers = innings_data.get('bowler', [])
    
    if bowlers:
        bowling_rows = []
        for bowler in bowlers:
            bowling_rows.append({
                'Bowler': bowler.get('name', 'Unknown'),
                'Overs': bowler.get('overs', '0'),
                'Maidens': bowler.get('maidens', 0),
                'Runs': bowler.get('runs', 0),
                'Wickets': bowler.get('wickets', 0),
                'Economy': bowler.get('economy', '0.00')
            })
        
        if bowling_rows:
            bowling_df = pd.DataFrame(bowling_rows)
            st.dataframe(bowling_df, use_container_width=True, hide_index=True)
        else:
            st.info("No bowling data")
    else:
        st.info("No bowling data available")
    
    # Extras
    extras = innings_data.get('extras', {})
    if extras:
        total = extras.get('total', 0)
        st.markdown(f"**Extras:** {total} (wd: {extras.get('wides', 0)}, nb: {extras.get('noballs', 0)}, lb: {extras.get('legbyes', 0)}, b: {extras.get('byes', 0)})")

def display_basic_match_info(match, team1, team2):
    """Display basic match info"""
    
    st.markdown("##### 📋 Match Information")
    
    # Convert date
    raw_date = match.get('match_date', 'N/A')
    formatted_date = convert_timestamp_to_date(raw_date)
    
    info_data = [
        {"Field": "Teams", "Value": f"{team1} vs {team2}"},
        {"Field": "Match ID", "Value": str(match.get('match_id', 'N/A'))},
        {"Field": "Date", "Value": formatted_date},
        {"Field": "Format", "Value": match.get('match_format', 'N/A')},
        {"Field": "Series", "Value": match.get('series_name', 'N/A')},
        {"Field": "Venue", "Value": match.get('venue', 'N/A')},
        {"Field": "City", "Value": match.get('city', 'N/A')},
        {"Field": "Status", "Value": match.get('status', 'N/A')},
        {"Field": "Type", "Value": match.get('match_type', 'N/A')}
    ]
    
    info_df = pd.DataFrame(info_data)
    st.dataframe(info_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    show()
