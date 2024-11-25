import streamlit as st
import pandas as pd
from itertools import combinations

# Load datasets with caching
@st.cache_data
def load_corr_data():
    return pd.read_csv('final_corr24.csv')

@st.cache_data
def load_game_logs():
    return pd.read_csv('game_logs_2024.csv')

# Load data
corr_data = load_corr_data()
game_logs = load_game_logs()

# Add tabs to Streamlit app
tab1, tab2, tab3 = st.tabs(["Player Correlations", "Game Log Query", "NHL Trios"])

### Tab 1: Existing Correlation Analysis
with tab1:
    st.title("NHL Player Correlations (2023 vs. 2024)")

    st.subheader("Filter by Player or Team")
    player = st.text_input("Search for Player", "")
    team = st.text_input("Search for Team", "")

    st.subheader("Credibility Filters")
    credibility_2024 = st.slider("2024 Credibility (Total Points A and Total Points B > X)", 
                                 min_value=0, 
                                 max_value=int(corr_data[['Total Points A', 'Total Points B']].max().max()), 
                                 value=0)
    credibility_2023 = st.slider("2023 Credibility (Total Points A_2023 and Total Points B_2023 > X)", 
                                 min_value=0, 
                                 max_value=int(corr_data[['Total Points A_2023', 'Total Points B_2023']].max().max()), 
                                 value=0)

    # Apply filters
    filtered_corr_data = corr_data
    if player:
        filtered_corr_data = filtered_corr_data[
            (filtered_corr_data['Player A'].str.contains(player, case=False)) |
            (filtered_corr_data['Player B'].str.contains(player, case=False))
        ]
    if team:
        filtered_corr_data = filtered_corr_data[filtered_corr_data['Team'] == team]
    
    filtered_corr_data = filtered_corr_data[
        (filtered_corr_data['Total Points A'] > credibility_2024) & 
        (filtered_corr_data['Total Points B'] > credibility_2024)
    ]
    filtered_corr_data = filtered_corr_data[
        (filtered_corr_data['Total Points A_2023'] > credibility_2023) & 
        (filtered_corr_data['Total Points B_2023'] > credibility_2023)
    ]

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

    st.download_button(
        label="Download Filtered Game Logs",
        data=final_filtered_game_logs[['GameID', 'GameDate']].drop_duplicates().to_csv(index=False),
        file_name="filtered_game_logs.csv",
        mime="text/csv"
    )

### Tab 3: Trio Analysis
with tab3:
    st.title("NHL Trios Analysis")

    # Select a team from the unique list of teams
    st.subheader("Select a Team")
    teams = game_logs['TeamAbbrev'].unique()
    selected_team = st.selectbox("Choose a Team", sorted(teams))

    # Filter data to only include the selected team
    team_data = game_logs[game_logs['TeamAbbrev'] == selected_team]

    # Get all unique players from the selected team
    team_data['FullName'] = team_data['FirstName'] + " " + team_data['LastName']
    team_players = team_data['FullName'].unique()

    # Find all combinations of 3 players
    player_combinations = list(combinations(team_players, 3))

    # Calculate the number of games where all 3 players recorded at least 1 point
    trio_game_counts = []
    for trio in player_combinations:
        player_a, player_b, player_c = trio
        # Filter games where all 3 players recorded at least 1 point
        games_with_trio = team_data[
            ((team_data['FullName'] == player_a) & (team_data['Points'] >= 1)) |
            ((team_data['FullName'] == player_b) & (team_data['Points'] >= 1)) |
            ((team_data['FullName'] == player_c) & (team_data['Points'] >= 1))
        ]
        games_with_trio_count = (
            games_with_trio['GameID']
            .value_counts()
            .loc[lambda x: x >= 3]  # Ensure all 3 players have points in the same game
            .count()
        )
        trio_game_counts.append({'Trio': trio, 'Games': games_with_trio_count})

    # Convert to a DataFrame for display
    trio_results = pd.DataFrame(trio_game_counts)
    trio_results = trio_results.sort_values(by='Games', ascending=False)

    # Display the top trios
    st.write(f"Top Trios for {selected_team}")
    st.write(trio_results.head(10))

    st.download_button(
        label="Download Trio Results",
        data=trio_results.to_csv(index=False),
        file_name=f"{selected_team}_trio_results.csv",
        mime="text/csv"
    )
