"""
CRUD Operations Page - UPDATED FOR REAL DATA
Uses players_real table with actual Cricbuzz data
Create, Read, Update, Delete player records
"""

import streamlit as st
import pandas as pd
from utils.db_connection import execute_query, execute_update
from datetime import datetime

def show():
    """Display the CRUD Operations page"""
    st.markdown("**Title:** CRUD - Operations")
    st.markdown("**Subtitle:** Create, Update, Delete Player Records")
    st.info("✅ **Using Real Data:** All operations work with the `players_real` table containing actual Cricbuzz player data")

    # Display database stats
    display_database_stats()

    # Choose operation
    display_crud_operation_selector()

def display_database_stats():
    """Show current database statistics"""
    try:
        total_query = "SELECT COUNT(*) as count FROM players_real"
        total_result = execute_query(total_query)

        detailed_query = "SELECT COUNT(*) as count FROM players_real WHERE has_detailed_stats = 1"
        detailed_result = execute_query(detailed_query)

        if total_result is not None and detailed_result is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Players", total_result['count'].iloc[0])
            with col2:
                st.metric("✅ With Details", detailed_result['count'].iloc[0])
            with col3:
                st.metric("🗄️ Table", "players_real")
    except:
        pass

def display_crud_operation_selector():
    """Display CRUD operation selection"""
    st.markdown("### Choose an Option:")

    crud_options = {
        "1. Create": "create",
        "2. Read (View Players)": "read",
        "3. Update": "update",
        "4. Delete": "delete"
    }

    selected_operation = st.selectbox(
        "Select CRUD operation:",
        options=list(crud_options.keys()),
        index=0,
        key="crud_operation_selector",
        help="Choose the database operation you want to perform"
    )

    operation_type = crud_options[selected_operation]

    # Route to appropriate operation
    if operation_type == "create":
        display_create_operation()
    elif operation_type == "read":
        display_read_operation()
    elif operation_type == "update":
        display_update_operation()
    elif operation_type == "delete":
        display_delete_operation()

def display_create_operation():
    """Display A) Create operation - REAL DATA VERSION"""
    st.markdown("### A) Create Operation")
    st.markdown("#### ADD NEW PLAYER")
    st.info("💡 **Note:** You can add new players with their actual Cricbuzz data")

    # Create form with fields matching players_real table
    with st.form("add_new_player_form"):
        col1, col2 = st.columns(2)

        with col1:
            player_id = st.text_input(
                "Player ID:",
                placeholder="e.g., 12345",
                help="Unique player identifier (TEXT)"
            )

            player_name = st.text_input(
                "Player Name:",
                placeholder="Enter full player name",
                help="Full name of the player"
            )

            team_name = st.text_input(
                "Team Name:",
                placeholder="e.g., India, Mumbai Indians",
                help="Current team"
            )

            role = st.selectbox(
                "Role:",
                options=["Batsman", "Bowler", "All-rounder", "Wicket-keeper"],
                help="Primary playing role"
            )

            batting_style = st.selectbox(
                "Batting Style:",
                options=["Right-hand bat", "Left-hand bat"],
                help="Batting style"
            )

        with col2:
            bowling_style = st.text_input(
                "Bowling Style:",
                placeholder="e.g., Right-arm fast, Left-arm spin",
                help="Bowling style (if applicable)"
            )

            international_team = st.text_input(
                "International Team:",
                placeholder="e.g., India, Australia",
                help="International team"
            )

            date_of_birth = st.date_input(
                "Date of Birth:",
                help="Player's date of birth"
            )

            birth_place = st.text_input(
                "Birth Place:",
                placeholder="e.g., Mumbai, India",
                help="Place of birth"
            )

        # Submit button
        submitted = st.form_submit_button("+ Add Player", type="primary")

        if submitted:
            if player_id and player_name:
                create_new_player_record(
                    player_id, player_name, team_name, role,
                    batting_style, bowling_style, international_team,
                    str(date_of_birth), birth_place
                )
            else:
                st.error("❌ Player ID and Name are required!")

def create_new_player_record(player_id, player_name, team_name, role,
                             batting_style, bowling_style, international_team,
                             date_of_birth, birth_place):
    """Create new player record in players_real table"""
    try:
        # Check if player ID already exists
        check_query = "SELECT COUNT(*) as count FROM players_real WHERE player_id = ?"
        result = execute_query(check_query, (player_id,))

        if result is not None and result['count'].iloc[0] > 0:
            st.error(f"❌ Player ID {player_id} already exists! Please use a different ID.")
            return

        # Insert new player into players_real
        insert_query = """
        INSERT INTO players_real (
            player_id, player_name, team_name, role,
            batting_style, bowling_style, international_team,
            date_of_birth, birth_place, has_detailed_stats, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
        """

        success = execute_update(insert_query, (
            player_id, player_name, team_name, role,
            batting_style, bowling_style, international_team,
            date_of_birth, birth_place
        ))

        if success:
            st.success(f"✅ Player '{player_name}' added successfully to players_real!")
            st.balloons()

            # Show added record
            new_player = execute_query(
                "SELECT * FROM players_real WHERE player_id = ?",
                (player_id,)
            )
            if new_player is not None:
                st.dataframe(new_player, use_container_width=True, hide_index=True)
        else:
            st.error("❌ Failed to add player to database.")

    except Exception as e:
        st.error(f"❌ Error adding player: {str(e)}")

def display_read_operation():
    """Display B) Read operation - REAL DATA VERSION"""
    st.markdown("### B) Read (View Players) Operation")

    # Search player by name
    st.markdown("#### Search Player by Name")
    search_name = st.text_input(
        "Enter the player name:",
        placeholder="Enter player name",
        key="read_search_name"
    )

    # If search name provided, search for specific player
    if search_name:
        search_specific_player(search_name)

    # View all players section
    st.markdown("#### View All Players")

    if st.button("📋 Load All Players", key="load_all_players_button"):
        load_all_players()

def search_specific_player(search_name):
    """Search for specific player by name in players_real"""
    with st.spinner(f"Searching for '{search_name}'..."):
        query = """
        SELECT player_id, player_name, team_name, role, 
               batting_style, bowling_style, international_team,
               date_of_birth, birth_place, has_detailed_stats
        FROM players_real
        WHERE LOWER(player_name) LIKE LOWER(?)
        ORDER BY player_name
        """
        search_term = f"%{search_name}%"
        results = execute_query(query, (search_term,))

        if results is not None and not results.empty:
            st.success(f"✅ Found {len(results)} player(s) matching '{search_name}'")
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.warning(f"⚠️ No players found matching '{search_name}'")

def load_all_players():
    """Load all players from players_real table"""
    with st.spinner("Loading all players..."):
        query = """
        SELECT ROW_NUMBER() OVER (ORDER BY player_name) as s_no,
               player_id, player_name, team_name, role,
               batting_style, bowling_style, international_team,
               CASE WHEN has_detailed_stats = 1 THEN '✅' ELSE '❌' END as details
        FROM players_real
        ORDER BY player_name
        """
        all_players = execute_query(query)

        if all_players is not None and not all_players.empty:
            st.success(f"✅ All players shown ({len(all_players)} players from players_real)")

            # Display in Excel sheet format
            st.dataframe(all_players, use_container_width=True, hide_index=True)

            # Export option
            csv_data = all_players.to_csv(index=False)
            st.download_button(
                "📥 Export All Players",
                csv_data,
                file_name="players_real_export.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ No players found in database")

def display_update_operation():
    """Display C) Update operation - REAL DATA VERSION"""
    st.markdown("### C) Update Operation")
    st.markdown("#### Update Player Record")

    # 1. Search for the player to update
    st.markdown("##### 1. Search for the player to update:")
    update_search_name = st.text_input(
        "Enter the player name to update:",
        placeholder="Enter player name",
        key="update_search_name"
    )

    if update_search_name and len(update_search_name) >= 3:
        search_player_for_update(update_search_name)

def search_player_for_update(search_name):
    """Search player for update operation"""
    query = """
    SELECT player_id, player_name, team_name, role,
           batting_style, bowling_style, international_team,
           date_of_birth, birth_place
    FROM players_real
    WHERE LOWER(player_name) LIKE LOWER(?)
    ORDER BY player_name
    """
    results = execute_query(query, (f"%{search_name}%",))

    if results is not None and not results.empty:
        # 2. Selected player to be updated
        st.markdown("##### 2. Selected player to be updated:")

        # Player selection
        player_options = {}
        for _, player in results.iterrows():
            display_name = f"{player['player_name']} (ID: {player['player_id']})"
            player_options[display_name] = player.to_dict()

        selected_player_name = st.selectbox(
            "Select player to update:",
            options=list(player_options.keys()),
            key="update_player_selector"
        )

        if selected_player_name:
            selected_player = player_options[selected_player_name]
            display_update_form(selected_player)
    else:
        st.warning(f"⚠️ No players found matching '{search_name}'")

def display_update_form(player):
    """Display update form with editable fields"""
    st.markdown("##### Details of the player in editable format:")

    # Display details in editable format
    with st.form("update_player_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Player ID:", value=str(player['player_id']), disabled=True)
            new_player_name = st.text_input("Player Name:", value=player['player_name'])
            new_team_name = st.text_input("Team Name:", value=player['team_name'] if player['team_name'] else "")
            new_role = st.text_input("Role:", value=player['role'] if player['role'] else "")
            new_batting_style = st.text_input("Batting Style:", value=player['batting_style'] if player['batting_style'] else "")

        with col2:
            new_bowling_style = st.text_input("Bowling Style:", value=player['bowling_style'] if player['bowling_style'] else "")
            new_international_team = st.text_input("International Team:", value=player['international_team'] if player['international_team'] else "")
            new_date_of_birth = st.text_input("Date of Birth:", value=player['date_of_birth'] if player['date_of_birth'] else "")
            new_birth_place = st.text_input("Birth Place:", value=player['birth_place'] if player['birth_place'] else "")

        # 3. Update button
        update_submitted = st.form_submit_button("🔄 Update Details", type="primary")

        if update_submitted:
            update_player_details(
                player['player_id'], new_player_name, new_team_name,
                new_role, new_batting_style, new_bowling_style,
                new_international_team, new_date_of_birth, new_birth_place
            )

def update_player_details(player_id, player_name, team_name, role,
                          batting_style, bowling_style, international_team,
                          date_of_birth, birth_place):
    """Update player details in players_real table"""
    try:
        update_query = """
        UPDATE players_real SET
            player_name = ?, team_name = ?, role = ?,
            batting_style = ?, bowling_style = ?, international_team = ?,
            date_of_birth = ?, birth_place = ?, last_updated = CURRENT_TIMESTAMP
        WHERE player_id = ?
        """

        success = execute_update(update_query, (
            player_name, team_name, role, batting_style, bowling_style,
            international_team, date_of_birth, birth_place, player_id
        ))

        if success:
            st.success(f"✅ Updated data saved to players_real for '{player_name}'!")

            # Show updated record
            updated_player = execute_query(
                "SELECT * FROM players_real WHERE player_id = ?",
                (player_id,)
            )
            if updated_player is not None:
                st.dataframe(updated_player, use_container_width=True, hide_index=True)
        else:
            st.error("❌ Failed to update player details.")

    except Exception as e:
        st.error(f"❌ Error updating player: {str(e)}")

def display_delete_operation():
    """Display D) Delete operation - REAL DATA VERSION"""
    st.markdown("### D) Delete Operation")
    st.markdown("#### Delete Player Record")

    # Warning message
    st.warning("⚠️ **Warning:** This action cannot be undone. Player will be permanently deleted from players_real table.")

    # 1. Search for the player to delete
    st.markdown("##### 1. Search for the player to delete:")
    delete_search_name = st.text_input(
        "Enter the player name to delete:",
        placeholder="Enter player name",
        key="delete_search_name"
    )

    if delete_search_name and len(delete_search_name) >= 3:
        search_player_for_delete(delete_search_name)

def search_player_for_delete(search_name):
    """Search player for delete operation"""
    query = """
    SELECT player_id, player_name, team_name, role,
           batting_style, bowling_style, international_team
    FROM players_real
    WHERE LOWER(player_name) LIKE LOWER(?)
    ORDER BY player_name
    """
    results = execute_query(query, (f"%{search_name}%",))

    if results is not None and not results.empty:
        # 2. Selected player to be deleted
        st.markdown("##### 2. Selected player to be deleted:")

        # Player selection
        player_options = {}
        for _, player in results.iterrows():
            display_name = f"{player['player_name']} (ID: {player['player_id']})"
            player_options[display_name] = player.to_dict()

        selected_player_name = st.selectbox(
            "Select player to delete:",
            options=list(player_options.keys()),
            key="delete_player_selector"
        )

        if selected_player_name:
            selected_player = player_options[selected_player_name]
            display_delete_confirmation(selected_player)
    else:
        st.warning(f"⚠️ No players found matching '{search_name}'")

def display_delete_confirmation(player):
    """Display delete confirmation"""
    player_name = player['player_name']

    st.markdown(f"##### You are about to delete {player_name}")

    # Show player details
    player_df = pd.DataFrame([player])
    st.dataframe(player_df, use_container_width=True, hide_index=True)

    # Type "delete [name]" to confirm
    st.markdown(f"##### Type 'delete {player_name}' to confirm:")
    confirmation_text = st.text_input(
        f"Type 'delete {player_name}' to confirm:",
        key="delete_confirmation_input",
        placeholder=f"delete {player_name}"
    )

    # Confirm delete button
    expected_text = f"delete {player_name}"
    if confirmation_text == expected_text:
        if st.button("🗑️ Confirm Delete", type="secondary", key="confirm_delete_button"):
            delete_player_record(player['player_id'], player_name)
    else:
        st.button("🗑️ Confirm Delete", disabled=True, 
                 help=f"Type 'delete {player_name}' to enable deletion")

def delete_player_record(player_id, player_name):
    """Delete player record from players_real table"""
    try:
        delete_query = "DELETE FROM players_real WHERE player_id = ?"
        success = execute_update(delete_query, (player_id,))

        if success:
            st.success(f"✅ Player '{player_name}' (ID: {player_id}) has been deleted from players_real!")
            st.info("The player record has been permanently removed from the database.")
        else:
            st.error("❌ Failed to delete player.")

    except Exception as e:
        st.error(f"❌ Error deleting player: {str(e)}")

if __name__ == "__main__":
    show()
