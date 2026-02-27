"""
Data Processing section from notebook modified for app
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Datasets:
    matches: pd.DataFrame
    team_matches: pd.DataFrame
    team_summary: pd.DataFrame
    home_away_points: pd.DataFrame
    delta_points: pd.DataFrame


def load_datasets() -> Datasets:
    data_dir = Path(__file__).resolve().parents[1] / "data"

    df_2324 = pd.read_csv(data_dir / "PL-season-2324.csv")
    df_2425 = pd.read_csv(data_dir / "PL-season-2425.csv")

    df_2324["season"] = "2023-24"
    df_2425["season"] = "2024-25"

    matches = pd.concat([df_2324, df_2425], ignore_index=True)
    matches["Date"] = pd.to_datetime(
        matches["Date"], dayfirst=True, format="mixed"
    )

    matches["home_points"] = np.where(
        matches["FTR"] == "H",
        3,
        np.where(matches["FTR"] == "D", 1, 0),
    )
    matches["away_points"] = np.where(
        matches["FTR"] == "A",
        3,
        np.where(matches["FTR"] == "D", 1, 0),
    )

    matches["total_goals"] = matches["FTHG"] + matches["FTAG"]
    matches["goal_diff"] = matches["FTHG"] - matches["FTAG"]

    matches["match_id"] = (
        matches["season"].astype(str)
        + "|"
        + matches["Date"].dt.strftime("%Y-%m-%d")
        + "|"
        + matches["HomeTeam"].astype(str)
        + "|"
        + matches["AwayTeam"].astype(str)
    )

    home_rows = matches[
        [
            "match_id",
            "season",
            "Date",
            "HomeTeam",
            "AwayTeam",
            "Referee",
            "FTHG",
            "FTAG",
            "home_points",
            "away_points",
            "HS",
            "HST",
            "HF",
            "HC",
            "HY",
            "HR",
        ]
    ].copy()

    home_rows.rename(
        columns={
            "HomeTeam": "Team",
            "AwayTeam": "Opponent",
            "FTHG": "GF",
            "FTAG": "GA",
            "home_points": "Points",
            "HS": "Shots",
            "HST": "SOT",
            "HF": "Fouls",
            "HC": "Corners",
            "HY": "Yellow",
            "HR": "Red",
        },
        inplace=True,
    )
    home_rows["Venue"] = "Home"

    away_rows = matches[
        [
            "match_id",
            "season",
            "Date",
            "HomeTeam",
            "AwayTeam",
            "Referee",
            "FTHG",
            "FTAG",
            "home_points",
            "away_points",
            "AS",
            "AST",
            "AF",
            "AC",
            "AY",
            "AR",
        ]
    ].copy()

    away_rows.rename(
        columns={
            "AwayTeam": "Team",
            "HomeTeam": "Opponent",
            "FTAG": "GF",
            "FTHG": "GA",
            "away_points": "Points",
            "AS": "Shots",
            "AST": "SOT",
            "AF": "Fouls",
            "AC": "Corners",
            "AY": "Yellow",
            "AR": "Red",
        },
        inplace=True,
    )
    away_rows["Venue"] = "Away"

    team_matches = pd.concat([home_rows, away_rows], ignore_index=True)
    team_matches["GD"] = team_matches["GF"] - team_matches["GA"]
    team_matches["Win"] = (team_matches["Points"] == 3).astype(int)

    team_summary = team_matches.groupby(["season", "Team"], as_index=False).agg(
        Points=("Points", "sum"),
        GF=("GF", "sum"),
        GA=("GA", "sum"),
        GD=("GD", "sum"),
        Wins=("Win", "sum"),
        Matches=("match_id", "nunique"),
    )

    home_away_points = team_matches.groupby(
        ["season", "Team", "Venue"],
        as_index=False,
    ).agg(Points=("Points", "sum"))

    wide = team_summary.pivot(
        index="Team", columns="season", values="Points"
    ).reset_index()
    wide["delta_points"] = wide["2024-25"] - wide["2023-24"]
    wide["Direction"] = np.where(wide["delta_points"] >= 0, "Rise", "Fall")

    valid_delta = wide.dropna(subset=["delta_points"])
    top_team = valid_delta.loc[valid_delta["delta_points"].idxmax(), "Team"]
    bottom_team = valid_delta.loc[valid_delta["delta_points"].idxmin(), "Team"]
    wide["is_extreme"] = wide["Team"].isin([top_team, bottom_team])

    return Datasets(
        matches=matches,
        team_matches=team_matches,
        team_summary=team_summary,
        home_away_points=home_away_points,
        delta_points=wide,
    )
