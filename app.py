import streamlit as st
import pandas as pd

# Load datasets with caching
@st.cache_data
def load_corr_data():
    return pd.read_csv('final_corr24.csv')

@st.cache_data
def load_game_logs():
    return pd.read_csv('game_logs_2024.csv')

corr_data = load_corr_data()
game_logs = load_game_logs()

# Add tabs to Streamlit app
tab1, tab2 = st.tabs(["Player Correlations", "Game Log Query"])

### Tab 1: Existing Correlation Analysis
with tab1:
    st.title("NHL Player Correlations (2023 vs. 2024)")

    # Existing code for player correlations goes here...
    st.subheader("Filter by Player or Team")
    player = st.text_input("Search for Player", "")
    team = st.text_input("Search for Team", "")

    st.subheader("Credibility Filters")
    credibility_2024 = st.slider("2024 Credibility (Total Points A and Total Points B > X)", min_value=0, max_value=int(corr_data[['Total Points A', 'Total Points B']].max().max()), value=0)
    credibility_2023 = st.slider("2023 Credibility (Total Points A_2023 and Total Points B_2023 > X)", min_value=0, max_value=int(corr_data[['Total Points A_2023', 'Total Points B_2023']].max().max()), value=0)

    filtered_corr_data = corr_data
    if player:
        filtered_corr_data = filtered_corr_data[(filtered_corr_data['Player A'].str.contains(player, case=False)) |
                                                (filtered_corr_data['Player B'].str.contains(player, case=False))]
    if team:
        filtered_corr_data = filtered_corr_data[(filtered_corr_data['Team'] == team)]
    
    filtered_corr_data = filtered_corr_data[(filtered_corr_data['Total Points A'] > credibility_2024) & 
                                            (filtered_corr_data['Total Points B'] > credibility_2024)]
    filtered_corr_data = filtered_corr_data[(filtered_corr_data['Total Points A_2023'] > credibility_2023) & 
                                            (filtered_corr_data['Total Points B_2023'] > credibility_2023)]

    st.write("Filtered Data", filtered_corr_data)

    st.download_button(
        label="Download Filtered Data",
        data=filtered_corr_data.to_csv(index=False),
        file_name="filtered_corr_data.csv",
        mime="text/csv"
    )

### Tab 2: Game Log Query
with tab2:
    st.title("Game Log Query (2024)")

    # Select player and criteria for Goals, Assists, and Points
    st.subheader("Filter by Player Performance")

    # Get unique player names for dropdowns
    game_logs['FullName'] = game_logs['FirstName'] + " " + game_logs['LastName']
    unique_players = game_logs['FullName'].unique()

    # Filtering inputs for Goals, Assists, Points
    col1, col2, col3 = st.columns(3)

    with col1:
        player_goals = st.selectbox("Player for Goals", unique_players, key="goals_player")
        min_goals = st.number_input("Minimum Goals", min_value=0, value=1, step=1, key="goals_filter")

    with col2:
        player_assists = st.selectbox("Player for Assists", unique_players, key="assists_player")
        min_assists = st.number_input("Minimum Assists", min_value=0, value=1, step=1, key="assists_filter")

    with col3:
        player_points = st.selectbox("Player for Points", unique_players, key="points_player")
        min_points = st.number_input("Minimum Points", min_value=0, value=1, step=1, key="points_filter")

    # Filter data based on user input
    filtered_game_logs = game_logs[
        ((game_logs['FullName'] == player_goals) & (game_logs['Goals'] >= min_goals)) |
        ((game_logs['FullName'] == player_assists) & (game_logs['Assists'] >= min_assists)) |
        ((game_logs['FullName'] == player_points) & (game_logs['Points'] >= min_points))
    ]

    # Show results
    st.write("Filtered Game Logs")
    st.write(filtered_game_logs[['GameID', 'GameDate']])

    # Download button for filtered game logs
    st.download_button(
        label="Download Filtered Game Logs",
        data=filtered_game_logs[['GameID', 'GameDate']].to_csv(index=False),
        file_name="filtered_game_logs.csv",
        mime="text/csv"
    )

