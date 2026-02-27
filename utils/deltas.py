"""
New to the Story - Deltas
"""

import numpy as np
import pandas as pd

from src.constants import SEASON_ORDER


def team_delta(team_summary: pd.DataFrame, team: str) -> tuple[float, float, float]:
    t = team_summary.loc[team_summary["Team"] == team, ["season", "Points"]].copy()
    points = t.set_index("season")["Points"]
    p2324 = float(points.get("2023-24", np.nan))
    p2425 = float(points.get("2024-25", np.nan))
    return p2324, p2425, p2425 - p2324


def home_away_delta(home_away_points: pd.DataFrame, team: str) -> dict:
    t = home_away_points.loc[home_away_points["Team"] == team].copy()
    wide = t.pivot(index="season", columns="Venue", values="Points").reindex(SEASON_ORDER)

    home_23 = float(wide.loc["2023-24", "Home"])
    home_24 = float(wide.loc["2024-25", "Home"])
    away_23 = float(wide.loc["2023-24", "Away"])
    away_24 = float(wide.loc["2024-25", "Away"])

    home_change = home_24 - home_23
    away_change = away_24 - away_23
    total_change = home_change + away_change

    if abs(home_change - away_change) <= 3:
        driver = "balanced"
    elif abs(home_change) > abs(away_change):
        driver = "home-driven"
    else:
        driver = "away-driven"

    return {
        "home_23": home_23,
        "home_24": home_24,
        "away_23": away_23,
        "away_24": away_24,
        "home_change": home_change,
        "away_change": away_change,
        "total_change": total_change,
        "driver": driver,
    }