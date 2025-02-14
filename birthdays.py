import pandas as pd
import requests
import time

def get_player_info(mlbam_id):
    """Fetch player age and position from MLB Stats API"""
    url = f"https://statsapi.mlb.com/api/v1/people/{mlbam_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('people') and len(data['people']) > 0:
            player = data['people'][0]
            birth_date = player.get('birthDate')
            position = player.get('primaryPosition', {}).get('abbreviation')
            
            result = {}
            if birth_date:
                birth_time = pd.to_datetime(birth_date)
                now = pd.Timestamp.now()
                age = (now - birth_time).days / 365.25
                result['Age'] = round(age, 1)
            if position:
                result['Position'] = position
                
            return result
        return {}
    except Exception as e:
        print(f"Error fetching data for MLBAMID {mlbam_id}: {str(e)}")
        return {}

def process_file(filename):
    """Process a single CSV file"""
    df = pd.read_csv(filename)
    is_hitters = 'hitters' in filename.lower()
    
    # Initialize columns
    df['Age'] = None
    if is_hitters:
        df['Position'] = None
    
    # Iterate through each row and fetch info
    for index, row in df.iterrows():
        mlbam_id = row['MLBAMID']
        player_info = get_player_info(mlbam_id)
        
        if 'Age' in player_info:
            df.at[index, 'Age'] = player_info['Age']
            print(f"Added age {player_info['Age']} for player ID {mlbam_id}")
            
        if is_hitters and 'Position' in player_info:
            df.at[index, 'Position'] = player_info['Position']
            print(f"Added position {player_info['Position']} for player ID {mlbam_id}")
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(0.05)
    
    # Save the updated DataFrame back to the original file
    df.to_csv(filename, index=False)
    print(f"Process completed for {filename}")

def main():
    files = ['steamer600-hitters-2025.csv', 'steamer600-pitchers-2025.csv']
    for file in files:
        print(f"\nProcessing {file}...")
        process_file(file)
    print("\nAll files processed successfully.")

if __name__ == "__main__":
    main()
