import os
import csv
import pandas as pd
from collections import defaultdict

# Standardize IPL team names, mapping historical brands to modern successors
TEAM_MAPPING = {
    "Delhi Daredevils": "Delhi Capitals",
    "Delhi Capitals": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Punjab Kings": "Punjab Kings",
    "Deccan Chargers": "Sunrisers Hyderabad",
    "Sunrisers Hyderabad": "Sunrisers Hyderabad",
    "Royal Challengers Bengaluru": "Royal Challengers Bangalore",
    "Royal Challengers Bangalore": "Royal Challengers Bangalore",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Rising Pune Supergiant": "Rising Pune Supergiant",
    "Pune Warriors": "Pune Warriors",
    "Kochi Tuskers Kerala": "Kochi Tuskers Kerala",
    "Gujarat Lions": "Gujarat Lions",
    "Mumbai Indians": "Mumbai Indians",
    "Chennai Super Kings": "Chennai Super Kings",
    "Kolkata Knight Riders": "Kolkata Knight Riders",
    "Rajasthan Royals": "Rajasthan Royals",
    "Gujarat Titans": "Gujarat Titans",
    "Lucknow Super Giants": "Lucknow Super Giants"
}

def aggregate_cricsheet_data(cricsheet_dir="dataset/cricsheet", output_path="dataset/raw_dataset.csv"):
    if not os.path.exists(cricsheet_dir):
        raise FileNotFoundError(f"Cricsheet directory not found at '{cricsheet_dir}'")
        
    print(f"Scanning '{cricsheet_dir}' for match CSV files...")
    files = [f for f in os.listdir(cricsheet_dir) if f.endswith('.csv')]
    print(f"Found {len(files)} match files.")
    
    # Structure to hold player stats:
    # player_name -> dict of runs, balls_faced, dot_balls, dismissals, set of matches, set of innings, dict of teams
    player_data = defaultdict(lambda: {
        'runs': 0,
        'balls_faced': 0,
        'dot_balls': 0,
        'dismissals': 0,
        'matches': set(),
        'innings': set(),
        'teams': defaultdict(int)
    })
    
    # We will process files in alphabetical/numerical order to keep it deterministic
    files.sort()
    
    for idx, f in enumerate(files):
        match_id = os.path.splitext(f)[0]
        path = os.path.join(cricsheet_dir, f)
        
        # Keep track of squads from info lines
        squad_players = {}
        
        with open(path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row:
                    continue
                
                # Check for squad mapping info
                if row[0] == 'info' and row[1] == 'player':
                    team_raw = row[2]
                    player_name = row[3]
                    team = TEAM_MAPPING.get(team_raw, team_raw)
                    squad_players[player_name] = team
                    
                elif row[0] == 'ball':
                    # Ensure standard column size (16 columns)
                    if len(row) < 16:
                        row = row + [''] * (16 - len(row))
                        
                    innings_num = row[1]
                    over_ball = row[2]
                    batting_team_raw = row[3]
                    batsman = row[4]
                    non_striker = row[5]
                    bowler = row[6]
                    
                    try:
                        runs_off_bat = int(row[7])
                    except ValueError:
                        runs_off_bat = 0
                        
                    wides = row[9]
                    wicket_type = row[14]
                    dismissed_player = row[15]
                    
                    batting_team = TEAM_MAPPING.get(batting_team_raw, batting_team_raw)
                    
                    # Wides do not count as valid balls faced by the batsman
                    is_wide = wides != '' and wides != '0'
                    
                    # Track that players were involved in this match
                    player_data[batsman]['matches'].add(match_id)
                    player_data[batsman]['innings'].add(match_id)
                    player_data[batsman]['teams'][batting_team] += 1
                    
                    player_data[non_striker]['matches'].add(match_id)
                    player_data[non_striker]['teams'][batting_team] += 0.01 # minor weight to non-striker
                    
                    player_data[bowler]['matches'].add(match_id)
                    
                    if not is_wide:
                        player_data[batsman]['balls_faced'] += 1
                        if runs_off_bat == 0:
                            player_data[batsman]['dot_balls'] += 1
                            
                    player_data[batsman]['runs'] += runs_off_bat
                    
                    # Track dismissals
                    if dismissed_player:
                        player_data[dismissed_player]['dismissals'] += 1
                        player_data[dismissed_player]['matches'].add(match_id)
                        
        # Associate players from squad lines that didn't bat or bowl
        for p_name, p_team in squad_players.items():
            player_data[p_name]['matches'].add(match_id)
            player_data[p_name]['teams'][p_team] += 0.05 # minor weight for squad presence
            
    print("Aggregation complete. Formatting records...")
    
    records = []
    for player, stats in player_data.items():
        # Clean up team: find team with most ball/squad involvements
        if stats['teams']:
            primary_team = max(stats['teams'].items(), key=lambda x: x[1])[0]
        else:
            primary_team = "Unknown"
            
        records.append({
            "Player_Name": player,
            "Team": primary_team,
            "Matches": len(stats['matches']),
            "Innings": len(stats['innings']),
            "Runs": stats['runs'],
            "Balls_Faced": stats['balls_faced'],
            "Dot_Balls": stats['dot_balls'],
            "Dismissals": stats['dismissals']
        })
        
    df = pd.DataFrame(records)
    
    # Save raw dataset
    df.to_csv(output_path, index=False)
    print(f"✔ Raw dataset of {len(df)} players saved to '{output_path}'")
    return df

if __name__ == "__main__":
    aggregate_cricsheet_data()
