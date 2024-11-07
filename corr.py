import pandas as pd
import xlsxwriter

teams = ["ANA", "UTH", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET", 
     "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", 
     "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WPG"]

# Read in game_logs.csv
df_game_logs = pd.read_csv('game_logs_2024.csv')

# Step 1: Filter data to include only relevant columns and ensure game logs are sorted by date
df_filtered = df_game_logs[['GameDate', 'TeamAbbrev', 'PlayerID', 'FirstName', 'LastName', 'Points']]

# Step 2: Create a unique player identifier and pivot the data
df_filtered['PlayerName'] = df_filtered['FirstName'] + ' ' + df_filtered['LastName']
df_pivot = df_filtered.pivot_table(index=['GameDate', 'TeamAbbrev'], columns='PlayerName', values='Points')

# Step 3: Calculate correlations for each team and save to Excel
team_correlations = {}
correlation_list = []

# Create a Pandas Excel writer using XlsxWriter as the engine.
with pd.ExcelWriter('team_correlations.xlsx', engine='xlsxwriter') as writer:
    for team in df_pivot.index.get_level_values('TeamAbbrev').unique():
        team_data = df_pivot.xs(team, level='TeamAbbrev')

        # Filter team_data to only include columns for players in that team
        team_players = df_filtered[df_filtered['TeamAbbrev'] == team]['PlayerName'].unique()
        team_data = team_data[team_players]

        # Calculate the pairwise correlation between players' points for the team
        correlation_matrix = team_data.corr().round(2)
        team_correlations[team] = correlation_matrix

        # Write the correlation matrix to the Excel sheet
        correlation_matrix.to_excel(writer, sheet_name=team)

        # Extract the correlations and add to the correlation list
        for player1 in correlation_matrix.columns:
            for player2 in correlation_matrix.index:
                if player1 != player2:
                    correlation_value = correlation_matrix.loc[player1, player2]
                    total_points_a = df_filtered[df_filtered['PlayerName'] == player1]['Points'].sum()
                    total_points_b = df_filtered[df_filtered['PlayerName'] == player2]['Points'].sum()
                    correlation_list.append((team, player1, player2, correlation_value, total_points_a, total_points_b))

# Sort the correlation list by correlation value in descending order
sorted_correlations = sorted(correlation_list, key=lambda x: x[3], reverse=True)

# Save the highest correlations to a CSV file
correlation_df = pd.DataFrame(sorted_correlations, columns=['Team', 'Player A', 'Player B', 'Correlation', 'Total Points A', 'Total Points B'])

# Sort Player A and Player B alphabetically within each row
correlation_df[['Player A', 'Player B']] = correlation_df[['Player A', 'Player B']].apply(lambda x: sorted(x), axis=1, result_type='expand')

# Remove duplicate pairs
correlation_df = correlation_df.drop_duplicates(subset=['Player A', 'Player B'])

#Sort by Correlation descending
correlation_df = correlation_df.sort_values(by='Correlation', ascending=False)
#Filter for Total points A and B > 5
#correlation_df = correlation_df[(correlation_df['Total Points A'] > 10) & (correlation_df['Total Points B'] > 10)]

correlation_df['pair_id'] = correlation_df['Player A'] + '-' + correlation_df['Player B']

correlation_df.to_csv('top_player_correlations24.csv', index=False)