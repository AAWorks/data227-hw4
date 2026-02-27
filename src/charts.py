"""
Reused charts from the dashboard
"""

import altair as alt
import pandas as pd

from .constants import SEASON_ORDER


def chart_delta_points(
        delta_points: pd.DataFrame,
        selected_team: str
) -> alt.Chart:
    df = delta_points.dropna(subset=["delta_points"]).copy()
    df = df.sort_values("delta_points", ascending=True)
    df["Selected"] = df["Team"].eq(selected_team)

    team_click = alt.selection_point(
        name="delta_pick",
        fields=["Team"],
        on="click",
        clear="dblclick",
        empty=False,
    )

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(
                "delta_points:Q",
                title="Delta points (2024-25 minus 2023-24)"
            ),
            y=alt.Y("Team:N", sort=alt.SortField(
                "delta_points",
                order="ascending"
            ), title=None),
            color=alt.condition(
                alt.datum.Selected,
                alt.value("#111827"),
                alt.Color(
                    "Direction:N",
                    scale=alt.Scale(
                        domain=["Rise", "Fall"],
                        range=["#1f77b4", "#d62728"]
                    ),
                    legend=alt.Legend(title=None, orient="top"),
                ),
            ),
            tooltip=[
                "Team:N",
                alt.Tooltip("2023-24:Q", title="Points 2023-24"),
                alt.Tooltip("2024-25:Q", title="Points 2024-25"),
                alt.Tooltip(
                    "delta_points:Q",
                    title="Delta points",
                    format="+.0f"
                ),
            ],
        )
        .add_params(team_click)
        .properties(height=720, title="Biggest swings in points")
    )


def chart_points_by_team(
        team_summary: pd.DataFrame,
        selected_team: str
) -> alt.Chart:
    df = team_summary.copy()
    df["Selected"] = df["Team"].eq(selected_team)

    base = alt.Chart(df).encode(
        x=alt.X("Points:Q", title="Total points"),
        y=alt.Y("Team:N", sort="-x", title=None),
        tooltip=["season:N", "Team:N", "Points:Q", "Wins:Q", "GD:Q"],
    )

    points = base.mark_circle(size=75).encode(
        color=alt.condition(
            alt.datum.Selected,
            alt.value("#1f77b4"),
            alt.value("#d1d5db")
        )
    )

    highlight = (
        base.transform_filter(alt.datum.Selected)
        .mark_circle(size=170, filled=False, stroke="#111827", strokeWidth=2)
    )

    return (
        alt.layer(points, highlight)
        .facet(column=alt.Column("season:N", sort=SEASON_ORDER, title=None))
        .properties(title="Q1: team points by season")
    )


def chart_home_away_points(
        home_away_points: pd.DataFrame,
        selected_team: str
) -> alt.Chart:
    df = home_away_points.copy()
    df["Selected"] = df["Team"].eq(selected_team)

    return (
        alt.Chart(df)
        .properties(height=420)
        .mark_bar()
        .encode(
            x=alt.X("Points:Q", title="Points"),
            y=alt.Y("Team:N", sort="-x", title=None),
            color=alt.Color(
                "Venue:N",
                scale=alt.Scale(
                    domain=["Home", "Away"],
                    range=["#f28e2b", "#4e79a7"]
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            opacity=alt.condition(
                alt.datum.Selected,
                alt.value(1.0),
                alt.value(0.25)
            ),
            tooltip=["season:N", "Team:N", "Venue:N", "Points:Q"],
        )
        .facet(column=alt.Column("season:N", sort=SEASON_ORDER, title=None))
        .properties(title="Q3: home vs away points by season")
    )


def chart_match_scatter(
        team_matches: pd.DataFrame,
        selected_team: str
) -> alt.Chart:
    df = team_matches.loc[team_matches["Team"] == selected_team].copy()

    max_goal = max(1, int(max(df["GF"].max(), df["GA"].max())))
    brush = alt.selection_interval(name="match_brush", encodings=["x", "y"])

    return (
        alt.Chart(df)
        .mark_circle(size=80)
        .encode(
            x=alt.X(
                "GF:Q",
                title="Goals for",
                scale=alt.Scale(domain=[-0.5, max_goal + 0.5])
            ),
            y=alt.Y(
                "GA:Q",
                title="Goals against",
                scale=alt.Scale(domain=[-0.5, max_goal + 0.5])
            ),
            color=alt.Color("season:N", sort=SEASON_ORDER),
            shape=alt.Shape("Venue:N"),
            opacity=alt.condition(brush, alt.value(0.95), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                "season:N",
                "Venue:N",
                "Opponent:N",
                "GF:Q",
                "GA:Q",
                "Points:Q",
            ],
        )
        .add_params(brush)
        .properties(
            height=420,
            title=f"Q4: Match outcomes for {selected_team} (click and drag to brush)",
        )
    )
