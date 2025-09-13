"""
CRUD Operations Page - Exact UI Implementation as Specified
Create, Read, Update, Delete player records with exact interface
"""

import streamlit as st
import pandas as pd
from utils.db_connection import execute_query, execute_update
from datetime import datetime

def show():
    """Display the CRUD Operations page with exact specifications"""

    # Page title (specified format)
    st.markdown("**Title:** CRUD - Operations")
    st.markdown("**Subtitle:** Create, Update, Delete Player Records")

    # Choose an option dropdown
    display_crud_operation_selector()

def display_crud_operation_selector():
    """Display CRUD operation selection with exact dropdown options"""

    st.markdown("### Choose an Option:")

    # Dropdown with exactly 4 operations as specified
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
    """Display A) Create operation with exact specifications"""

    st.markdown("### A) Create Operation")
    st.markdown("#### ADD NEW PLAYER")

    # Create form with exact fields as specified
    with st.form("add_new_player_form"):

        # Form fields as specified
        player_id = st.number_input(
            "Player ID:",
            min_value=1,
            max_value=9999,
            value=100,
            step=1,
            help="Enter the player ID"
        )

        player_name = st.text_input(
            "Player Name:",
            placeholder="Enter the player name",
            help="Enter the player name"
        )

        matches = st.number_input(
            "Matches:",
            min_value=0,
            max_value=500,
            value=0,
            step=1,
            help="Enter the matches"
        )

        innings = st.number_input(
            "Innings:",
            min_value=0,
            max_value=1000,
            value=0,
            step=1,
            help="Enter the innings"
        )

        runs = st.number_input(
            "Runs:",
            min_value=0,
            max_value=20000,
            value=0,
            step=1,
            help="Enter the runs"
        )

        average = st.number_input(
            "Average:",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            help="Enter the average"
        )

        # "+Add player" button as specified
        submitted = st.form_submit_button("+ Add Player", type="primary")

        if submitted:
            if player_name:
                create_new_player_record(player_id, player_name, matches, innings, runs, average)
            else:
                st.error("❌ Player name is required!")

def create_new_player_record(player_id, player_name, matches, innings, runs, average):
    """Create new player record in database"""

    try:
        # Check if player ID already exists
        check_query = "SELECT COUNT(*) as count FROM players WHERE player_id = ?"
        result = execute_query(check_query, (player_id,))

        if result is not None and result['count'].iloc[0] > 0:
            st.error(f"❌ Player ID {player_id} already exists! Please use a different ID.")
            return

        # Insert new player with details entered
        insert_query = """
        INSERT INTO players (
            player_id, player_name, matches_played, runs_scored, batting_average,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """

        success = execute_update(insert_query, (player_id, player_name, matches, runs, average))

        if success:
            st.success(f"✅ Player '{player_name}' added successfully with details entered into the database!")
            st.balloons()

            # Show added record
            new_player = execute_query("SELECT * FROM players WHERE player_id = ?", (player_id,))
            if new_player is not None:
                st.dataframe(new_player, use_container_width=True, hide_index=True)
        else:
            st.error("❌ Failed to add player to database.")

    except Exception as e:
        st.error(f"❌ Error adding player: {str(e)}")

def display_read_operation():
    """Display B) Read operation with exact specifications"""

    st.markdown("### B) Read (View Players) Operation")

    # Search player by name as specified
    st.markdown("#### Search Player by Name")
    search_name = st.text_input(
        "Enter the player name:",
        placeholder="Enter the player name",
        key="read_search_name"
    )

    # View all players section as specified
    st.markdown("#### View All Players")

    # "Load all players" button as specified
    if st.button("📋 Load All Players", key="load_all_players_button"):
        load_all_players()

    # If search name provided, search for specific player
    if search_name:
        search_specific_player(search_name)

def search_specific_player(search_name):
    """Search for specific player by name"""

    with st.spinner(f"Searching for '{search_name}'..."):
        query = """
        SELECT player_id, player_name, matches_played, runs_scored, batting_average
        FROM players 
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
    """Load all players in Excel sheet format with specified columns"""

    with st.spinner("Loading all players..."):
        # Excel sheet format with specified columns: s.no, player_id, player_name, matches, innings, runs, averages
        query = """
        SELECT ROW_NUMBER() OVER (ORDER BY player_name) as s_no,
               player_id, player_name, matches_played as matches, 
               matches_played as innings, runs_scored as runs, batting_average as averages
        FROM players 
        ORDER BY player_name
        """

        all_players = execute_query(query)

    if all_players is not None and not all_players.empty:
        st.success(f"✅ All players details shown in Excel sheet format ({len(all_players)} players)")

        # Display in Excel sheet format with specified columns
        st.dataframe(all_players, use_container_width=True, hide_index=True)

        # Export option
        csv_data = all_players.to_csv(index=False)
        st.download_button(
            "📥 Export All Players",
            csv_data,
            file_name="all_players_database.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No players found in database")

def display_update_operation():
    """Display C) Update operation with exact specifications"""

    st.markdown("### C) Update Operation")
    st.markdown("#### Update Player Record")

    # 1. Search for the player to update as specified
    st.markdown("##### 1. Search for the player to update:")
    update_search_name = st.text_input(
        "Enter the player name to be get updated his details:",
        placeholder="Enter the player name to be get updated his details",
        key="update_search_name"
    )

    if update_search_name and len(update_search_name) >= 3:
        search_player_for_update(update_search_name)

def search_player_for_update(search_name):
    """Search player for update operation"""

    query = """
    SELECT player_id, player_name, matches_played, runs_scored, batting_average
    FROM players 
    WHERE LOWER(player_name) LIKE LOWER(?)
    ORDER BY player_name
    """

    results = execute_query(query, (f"%{search_name}%",))

    if results is not None and not results.empty:
        # 2. Selected player to be updated as specified
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

    st.markdown("##### Details of the player in editable line editor:")

    # Display details in editable format as specified
    with st.form("update_player_form"):

        # Editable fields with current values
        new_s_no = st.text_input("S.No:", value="1", disabled=True)
        new_player_id = st.text_input("Player_ID:", value=str(player['player_id']), disabled=True)
        new_player_name = st.text_input("Player_Name:", value=player['player_name'])
        new_matches = st.number_input("Matches:", value=int(player['matches_played']) if player['matches_played'] else 0)
        new_innings = st.number_input("Innings:", value=int(player['matches_played']) if player['matches_played'] else 0)  # Mock innings
        new_runs = st.number_input("Runs:", value=int(player['runs_scored']) if player['runs_scored'] else 0)
        new_average = st.number_input("Average:", value=float(player['batting_average']) if player['batting_average'] else 0.0, format="%.2f")

        # 3. "Update details" button as specified
        update_submitted = st.form_submit_button("🔄 Update Details", type="primary")

        if update_submitted:
            update_player_details(player['player_id'], new_player_name, new_matches, new_runs, new_average)

def update_player_details(player_id, player_name, matches, runs, average):
    """Update player details in database"""

    try:
        update_query = """
        UPDATE players SET 
            player_name = ?, matches_played = ?, runs_scored = ?, 
            batting_average = ?, updated_at = CURRENT_TIMESTAMP
        WHERE player_id = ?
        """

        success = execute_update(update_query, (player_name, matches, runs, average, player_id))

        if success:
            st.success(f"✅ Updated data saved to the database for '{player_name}'!")

            # Show updated record
            updated_player = execute_query("SELECT * FROM players WHERE player_id = ?", (player_id,))
            if updated_player is not None:
                st.dataframe(updated_player, use_container_width=True, hide_index=True)
        else:
            st.error("❌ Failed to update player details.")

    except Exception as e:
        st.error(f"❌ Error updating player: {str(e)}")

def display_delete_operation():
    """Display D) Delete operation with exact specifications"""

    st.markdown("### D) Delete Operation")
    st.markdown("#### Delete Player Record")

    # Warning message as specified
    st.markdown("##### ⚠️ Warning: This action cannot be undone")

    # 1. Search for the player to delete as specified
    st.markdown("##### 1. Search for the player to delete:")
    delete_search_name = st.text_input(
        "Enter the player name to be get deleted his details:",
        placeholder="Enter the player name to be get deleted his details",
        key="delete_search_name"
    )

    if delete_search_name and len(delete_search_name) >= 3:
        search_player_for_delete(delete_search_name)

def search_player_for_delete(search_name):
    """Search player for delete operation"""

    query = """
    SELECT player_id, player_name, matches_played, runs_scored, batting_average
    FROM players 
    WHERE LOWER(player_name) LIKE LOWER(?)
    ORDER BY player_name
    """

    results = execute_query(query, (f"%{search_name}%",))

    if results is not None and not results.empty:
        # 2. Selected player to be deleted as specified
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
    """Display delete confirmation with exact specifications"""

    player_name = player['player_name']

    # Sub sub title as specified
    st.markdown(f"##### You are about to delete the {player_name} player")

    # Show player details
    player_df = pd.DataFrame([player])
    st.dataframe(player_df, use_container_width=True, hide_index=True)

    # Type "delete <player name>" to confirm as specified
    st.markdown(f"##### Type 'delete {player_name}' to confirm:")

    confirmation_text = st.text_input(
        f"Type 'delete {player_name}' to confirm:",
        key="delete_confirmation_input",
        placeholder=f"delete {player_name}"
    )

    # "Confirm delete" button as specified
    expected_text = f"delete {player_name}"

    if confirmation_text == expected_text:
        if st.button("🗑️ Confirm Delete", type="secondary", key="confirm_delete_button"):
            delete_player_record(player['player_id'], player_name)
    else:
        st.button("🗑️ Confirm Delete", disabled=True, help=f"Type 'delete {player_name}' to enable deletion")

def delete_player_record(player_id, player_name):
    """Delete player record from database"""

    try:
        delete_query = "DELETE FROM players WHERE player_id = ?"
        success = execute_update(delete_query, (player_id,))

        if success:
            st.success(f"✅ Player '{player_name}' (ID: {player_id}) has been deleted successfully!")
            st.info("The player record has been permanently removed from the database.")
        else:
            st.error("❌ Failed to delete player.")

    except Exception as e:
        st.error(f"❌ Error deleting player: {str(e)}")

if __name__ == "__main__":
    show()
