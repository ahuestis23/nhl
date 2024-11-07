import requests
import pandas as pd
import time

# List of NHL team abbreviations
teams = ["ANA", "UTA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET", 
         "EDM", "FLA", "LAK", "MIN", "MTL", "NSH", "NJD", "NYI", "NYR", "OTT", "PHI", 
         "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "VAN", "VGK", "WSH", "WPG"]

# Initialize a list to store player game log data
all_game_logs = []

# Loop through each team to get player rosters
for team in teams:
    roster_url = f"https://api-web.nhle.com/v1/roster/{team}/20242025"
    roster_response = requests.get(roster_url)

    if roster_response.status_code == 200:
        roster_data = roster_response.json()
        positions = ['forwards', 'defensemen']

        # Loop through each position group excluding goalies
        for position in positions:
            if position in roster_data:
                for player in roster_data[position]:
                    player_id = player['id']
                    position_code = player['positionCode']

                    # Check if player is not a goalie
                    if position_code not in ['G']:
                        # Game log endpoint for the player
                        game_log_url = f"https://api-web.nhle.com/v1/player/{player_id}/game-log/20242025/2"
                        game_log_response = requests.get(game_log_url)

                        # Proceed if game log data is successfully retrieved
                        if game_log_response.status_code == 200:
                            game_log_data = game_log_response.json()

                            # Loop through each game log entry for the player
                            for game in game_log_data['gameLog']:
                                game_info = {
                                    'PlayerID': player_id,
                                    'FirstName': player['firstName']['default'],
                                    'LastName': player['lastName']['default'],
                                    'TeamAbbrev': game['teamAbbrev'],
                                    'GameID': game['gameId'],
                                    'GameDate': game['gameDate'],
                                    'Goals': game['goals'],
                                    'Assists': game['assists'],
                                    'Points': game['points'],
                                    'PlusMinus': game['plusMinus'],
                                    'PowerPlayGoals': game['powerPlayGoals'],
                                    'PowerPlayPoints': game['powerPlayPoints'],
                                    'GameWinningGoals': game['gameWinningGoals'],
                                    'Shots': game['shots'],
                                    'Shifts': game['shifts'],
                                    'PIM': game['pim'],
                                    'TOI': game['toi'],
                                    'OpponentAbbrev': game['opponentAbbrev'],
                                    'HomeRoadFlag': game['homeRoadFlag']
                                }
                                all_game_logs.append(game_info)
                        else:
                            print(f"Failed to retrieve game log for player ID {player_id}")

                        # Optional: Add a short delay to avoid overloading the API
                        time.sleep(0.1)
    else:
        print(f"Failed to retrieve roster for team {team}")

# Convert all game log data to a DataFrame
df_game_logs = pd.DataFrame(all_game_logs)
print(df_game_logs)
df_game_logs.to_csv('game_logs_2024.csv', index=False)