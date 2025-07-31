#!/usr/bin/env python
# coding: utf-8

# In[1]:


from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerDashboardByYearOverYear
import pandas as pd
import time
import os
from datetime import datetime

csv_path = "nba_season_stats_all_players.csv"


def get_current_season():
    today = datetime.today()
    year = today.year
    month = today.month
    
    if month >= 10:
        return f"{year}-{str(year+1)[2:]}"
    else:
        return f"{year-1}-{str(year)[2:]}"

current_season = get_current_season()
print(f"Current NBA season: {current_season}")


if os.path.exists(csv_path):
    existing_df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"🔁 Loaded existing data: {len(existing_df)} rows")
else:
    existing_df = pd.DataFrame()
    print("🆕 No existing CSV found. Starting fresh.")


player_list = players.get_active_players()
player_map = {p['full_name']: p['id'] for p in player_list}


if 'PLAYER_ID' not in existing_df.columns and not existing_df.empty:
    print("Adding PLAYER_ID column to existing data...")
    existing_df['PLAYER_ID'] = existing_df['PLAYER_NAME'].map(player_map)


if 'SEASON_ID' in existing_df.columns:
    
    existing_df_filtered = existing_df[existing_df['SEASON_ID'] < current_season]
else:
    existing_df_filtered = existing_df

fetched_ids = set(existing_df_filtered['PLAYER_ID'].dropna().astype(int).unique()) if not existing_df_filtered.empty else set()

all_stats = [existing_df_filtered] if not existing_df_filtered.empty else []

print(f"Already fetched {len(fetched_ids)} players before {current_season}")


for i, player in enumerate(player_list):
    if player['id'] in fetched_ids:
        continue

    try:
        print(f"⏳ Fetching {player['full_name']} ({i+1}/{len(player_list)})")
        stats = PlayerDashboardByYearOverYear(player_id=player['id'])
        season_data = stats.get_data_frames()[1]

        
        season_data = season_data[season_data['SEASON_ID'] >= current_season]

        if season_data.empty:
            
            continue

        season_data['PLAYER_NAME'] = player['full_name']
        season_data['PLAYER_ID'] = player['id']

        all_stats.append(season_data)
        time.sleep(0.5)

    except Exception as e:
        print(f"❌ Failed for {player['full_name']}: {e}")
        continue

if all_stats:
    final_df = pd.concat(all_stats, ignore_index=True)
    final_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ Updated CSV saved: {csv_path} with {len(final_df)} rows")
else:
    print("⚠️ No new data to fetch or CSV unchanged.")

