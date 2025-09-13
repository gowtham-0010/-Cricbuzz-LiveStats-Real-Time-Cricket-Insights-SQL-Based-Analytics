"""
Live Matches Page - Simplified & Clean
Improved scorecard column names and reduced unnecessary text
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

def show():
    """Display the Live Scores page with simplified interface"""

    # Initialize session state
    if 'selected_match_index' not in st.session_state:
        st.session_state.selected_match_index = 0
    if 'show_scorecard' not in st.session_state:
        st.session_state.show_scorecard = False

    # Fetch all matches
    with st.spinner("Fetching match data..."):
        all_matches = get_all_matches()

    if not all_matches:
        st.error("❌ Unable to fetch match data from API")
        return

    st.success(f"✅ Found {len(all_matches)} matches")

    # Match selection
    st.markdown("### Select a Match")

    # Create display options
    match_display_options = []
    for match in all_matches:
        team1 = match.get('team1', 'Team 1')
        team2 = match.get('team2', 'Team 2')
        match_date = match.get('match_date', 'TBD')
        match_type = match.get('match_type', 'Match')

        display_text = f"{team1} vs {team2} - {match_date} ({match_type})"
        match_display_options.append(display_text)

    if not match_display_options:
        st.error("❌ No matches available")
        return

    # Ensure index is valid
    if st.session_state.selected_match_index >= len(all_matches):
        st.session_state.selected_match_index = 0

    # Selectbox
    selected_index = st.selectbox(
        "Choose a match:",
        range(len(match_display_options)),
        format_func=lambda x: match_display_options[x],
        index=st.session_state.selected_match_index
    )

    # Update session state
    if selected_index != st.session_state.selected_match_index:
        st.session_state.selected_match_index = selected_index
        st.session_state.show_scorecard = False

    # Get selected match
    selected_match = all_matches[selected_index]

    # Display sections
    display_match_details(selected_match)
    display_current_score_details(selected_match)  
    display_scorecard_section(selected_match, selected_index)

def display_match_details(match):
    """Display match details"""

    st.markdown("### Match Information")

    # Get match data
    team1 = match.get('team1', 'N/A')
    team2 = match.get('team2', 'N/A')
    series_name = match.get('series_name', 'N/A')
    match_date = match.get('match_date', 'N/A')
    match_format = match.get('match_format', 'N/A')
    venue = match.get('venue', 'N/A')
    city = match.get('city', 'N/A')
    status = match.get('status', 'N/A')
    match_type = match.get('match_type', 'N/A')

    # Title
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%); 
                padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0;">
        <h2 style="color: white; margin: 0;">{team1} vs {team2}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Match details in columns
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
    """Display current scores in cricket format"""

    st.markdown("### Current Scores")

    team1 = match.get('team1', 'Team 1')
    team2 = match.get('team2', 'Team 2')
    status = match.get('status', 'N/A')

    # Get team short names
    team1_short = get_team_short_name(team1)
    team2_short = get_team_short_name(team2)

    # Check for score data
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
            score_lines.append(f"**{team1_short}** = Innings 1: {runs}/{wickets} ({overs} overs)")

        if team1_inngs2:
            runs = team1_inngs2.get('runs', 0)
            wickets = team1_inngs2.get('wickets', 0)
            overs = team1_inngs2.get('overs', 0.0)
            score_lines.append(f"**{team1_short}** = Innings 2: {runs}/{wickets} ({overs} overs)")

        # Team 2 scores
        if team2_inngs1:
            runs = team2_inngs1.get('runs', 0)
            wickets = team2_inngs1.get('wickets', 0)
            overs = team2_inngs1.get('overs', 0.0)
            score_lines.append(f"**{team2_short}** = Innings 1: {runs}/{wickets} ({overs} overs)")

        if team2_inngs2:
            runs = team2_inngs2.get('runs', 0)
            wickets = team2_inngs2.get('wickets', 0)
            overs = team2_inngs2.get('overs', 0.0)
            score_lines.append(f"**{team2_short}** = Innings 2: {runs}/{wickets} ({overs} overs)")

        if score_lines:
            # Score container
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

    # Load scorecard button
    if st.button("🏏 Load Scorecard", key=f"load_btn_{match_index}"):
        st.session_state.show_scorecard = True

    if st.session_state.show_scorecard:
        if not match_id:
            st.error("❌ Match ID not available")
        else:
            with st.spinner("Loading scorecard..."):
                scorecard_data = get_match_scorecard(str(match_id))

            if scorecard_data:
                st.success("✅ Scorecard loaded")
                display_scorecard_tables(scorecard_data, team1, team2)
            else:
                st.warning("⚠️ Scorecard not available")
                display_basic_match_info(match, team1, team2)

        if st.button("❌ Hide Scorecard", key=f"hide_btn_{match_index}"):
            st.session_state.show_scorecard = False
            st.rerun()

def display_scorecard_tables(scorecard_data, team1, team2):
    """Display scorecard in clean table format with better column names"""

    st.markdown("#### 📊 Complete Scorecard")

    try:
        # Innings data
        innings = scorecard_data.get('innings', [])
        if innings:
            for i, inning in enumerate(innings):
                if isinstance(inning, dict):
                    # Batting scorecard with improved column names
                    batting_details = inning.get('batTeamDetails', {})
                    if batting_details:
                        team_name = batting_details.get('batTeamName', f'Team {i+1}')
                        st.markdown(f"##### 🏏 {team_name} - Batting")

                        bat_stats = batting_details.get('batsmenData', {})
                        if bat_stats:
                            batting_rows = []
                            for player_id, player_data in bat_stats.items():
                                if isinstance(player_data, dict):
                                    batting_rows.append({
                                        "Player": player_data.get('batName', 'Unknown'),
                                        "Runs": player_data.get('runs', 0),
                                        "Balls Faced": player_data.get('balls', 0),
                                        "Fours": player_data.get('fours', 0),
                                        "Sixes": player_data.get('sixes', 0),
                                        "Strike Rate": f"{player_data.get('strikeRate', 0.0):.1f}",
                                        "How Out": player_data.get('outDesc', 'Not Out')
                                    })

                            if batting_rows:
                                batting_df = pd.DataFrame(batting_rows)
                                st.dataframe(batting_df, use_container_width=True, hide_index=True)

                    # Bowling scorecard with improved column names
                    bowl_team_details = inning.get('bowlTeamDetails', {})
                    if bowl_team_details:
                        bowl_team_name = bowl_team_details.get('bowlTeamName', f'Bowling Team {i+1}')
                        st.markdown(f"##### ⚾ {bowl_team_name} - Bowling")

                        bowl_stats = bowl_team_details.get('bowlersData', {})
                        if bowl_stats:
                            bowling_rows = []
                            for bowler_id, bowler_data in bowl_stats.items():
                                if isinstance(bowler_data, dict):
                                    bowling_rows.append({
                                        "Bowler": bowler_data.get('bowlName', 'Unknown'),
                                        "Overs": f"{bowler_data.get('overs', 0)}",
                                        "Maiden Overs": bowler_data.get('maidens', 0),
                                        "Runs Given": bowler_data.get('runs', 0),
                                        "Wickets": bowler_data.get('wickets', 0),
                                        "Economy Rate": f"{bowler_data.get('economy', 0.0):.2f}",
                                        "Wides": bowler_data.get('wides', 0),
                                        "No Balls": bowler_data.get('noballs', 0)
                                    })

                            if bowling_rows:
                                bowling_df = pd.DataFrame(bowling_rows)
                                st.dataframe(bowling_df, use_container_width=True, hide_index=True)

                    st.markdown("---")

        # Match summary
        match_header = scorecard_data.get('match_header', {})
        if match_header:
            st.markdown("##### Match Summary")

            header_data = []
            for key, value in match_header.items():
                if isinstance(value, (str, int, float)):
                    # Improve field names
                    field_name = key.replace('_', ' ').title()
                    if 'toss' in key.lower():
                        field_name = "Toss Won By"
                    elif 'result' in key.lower():
                        field_name = "Match Result"
                    elif 'venue' in key.lower():
                        field_name = "Venue"

                    header_data.append({"Detail": field_name, "Information": str(value)})

            if header_data:
                header_df = pd.DataFrame(header_data)
                st.dataframe(header_df, use_container_width=True, hide_index=True)

        # Players of the match
        players_of_match = scorecard_data.get('players_of_match', [])
        if players_of_match:
            st.markdown("##### 🏆 Player Awards")

            player_rows = []
            for player in players_of_match:
                if isinstance(player, dict):
                    player_rows.append({
                        "Player Name": player.get('name', 'Unknown'),
                        "Team": player.get('team', 'Unknown'),
                        "Role": player.get('role', 'Unknown'),
                        "Award": player.get('performance', 'Player of the Match')
                    })

            if player_rows:
                players_df = pd.DataFrame(player_rows)
                st.dataframe(players_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ Error processing scorecard: {str(e)}")
        st.json(scorecard_data)

def display_basic_match_info(match, team1, team2):
    """Display basic match info when scorecard unavailable"""

    st.markdown("##### 📋 Match Information")

    info_data = [
        {"Field": "Teams", "Value": f"{team1} vs {team2}"},
        {"Field": "Date", "Value": match.get('match_date', 'N/A')},
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
