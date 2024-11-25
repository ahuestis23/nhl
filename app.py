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

    # Get unique player names and available markets
    game_logs['FullName'] = game_logs['FirstName'] + " " + game_logs['LastName']
    unique_players = game_logs['FullName'].unique()
    available_markets = ['Goals', 'Assists', 'Points', 'Shots']  # Add more markets as needed

    # Dynamic filtering mechanism
    st.subheader("Dynamic Market Filtering")
    num_filters = st.number_input("Number of Filters", min_value=1, max_value=5, value=3, step=1)

    filters = []
    for i in range(num_filters):
        st.write(f"Filter {i + 1}")
        player = st.selectbox(f"Select Player for Filter {i + 1}", unique_players, key=f"player_{i}")
        market = st.selectbox(f"Select Market for Filter {i + 1}", available_markets, key=f"market_{i}")
        threshold = st.number_input(f"Minimum {market} for Filter {i + 1}", min_value=0, value=1, step=1, key=f"threshold_{i}")
        filters.append({'player': player, 'market': market, 'threshold': threshold})

    # Apply filtering logic dynamically
    filtered_game_logs = pd.DataFrame()  # Placeholder for filtered rows
    for filter_item in filters:
        player = filter_item['player']
        market = filter_item['market']
        threshold = filter_item['threshold']

        # Filter rows matching the current filter
        condition = (game_logs['FullName'] == player) & (game_logs[market] >= threshold)
        filtered_game_logs = pd.concat([filtered_game_logs, game_logs[condition]])

    # Ensure all conditions are met in the same game
    game_ids_meeting_conditions = filtered_game_logs['GameID'].value_counts()
    valid_game_ids = game_ids_meeting_conditions[
        game_ids_meeting_conditions >= num_filters  # Must meet all conditions
    ].index

    final_filtered_game_logs = filtered_game_logs[filtered_game_logs['GameID'].isin(valid_game_ids)]

    # Display results
    st.write("Filtered Game Logs")
    st.write(final_filtered_game_logs[['GameID', 'GameDate']].drop_duplicates())

    # Download button for filtered game logs
    st.download_button(
        label="Download Filtered Game Logs",
        data=final_filtered_game_logs[['GameID', 'GameDate']].drop_duplicates().to_csv(index=False),
        file_name="filtered_game_logs.csv",
        mime="text/csv"
    )
