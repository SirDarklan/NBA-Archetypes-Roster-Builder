"""
Script to get the raw csvs into a data folder.
"""

import time
import pandas as pd

from pathlib import Path

# from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import (
    LeagueDashPlayerBioStats,
    LeagueDashPlayerStats,
    LeagueDashPlayerShotLocations,
    LeagueDashPtDefend,
    LeagueDashTeamStats,
    LeagueHustleStatsPlayer,
    PlayerGameLogs,
    PlayerIndex
)

SEASONS = ["2021-22",
           "2022-23",
           "2023-24",
           "2024-25",
           "2025-26"]
RS = "Regular Season"
OUT_PTH = "data/raw"
Path("data").mkdir(exist_ok=True) # Creating a directory for you.

def save(name, fetch):
    frames = []
    for s in SEASONS:
        df = fetch(s).get_data_frames()[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns=["_".join(c).strip("_") for c in df.columns]
            
        frames.append(df.assign(SEASON=s))
        time.sleep(1) # avoid rate limiting
        
    pd.concat(frames).to_csv(f"data/{name}.csv", index=False)
    print(name, "done.")
 
save("player_totals", lambda s: LeagueDashPlayerBioStats(season=s))
save("player_totals", lambda s: LeagueDashPlayerStats(season=s))
save("player_advanced", lambda s: LeagueDashPlayerStats(season=s, measure_type_detailed_defense="Advanced"))
save("player_scoring", lambda s: LeagueDashPlayerStats(season=s, measure_type_detailed_defense="Scoring"))
save("shot_zones", lambda s: LeagueDashPlayerShotLocations(season=s))
save("defend_rim", lambda s: LeagueDashPtDefend(season=s, defense_category="Less Than 6Ft"))
save("hustle", lambda s: LeagueHustleStatsPlayer(season=s))
save("player_index", lambda s: PlayerIndex(season=s))
save("game_logs", lambda s: PlayerGameLogs(season_nullable=s, season_type_nullable="Regular Season"))
save("team_stats", lambda s: LeagueDashTeamStats(season=s))