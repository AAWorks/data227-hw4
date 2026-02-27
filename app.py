import pandas as pd
import streamlit as st

from src import (
    load_datasets,
    chart_delta_points,
    chart_home_away_points,
    chart_match_scatter,
    chart_points_by_team,
)
from utils import (
    movement_sentence,
    match_callouts,
    team_delta,
    home_away_delta,
)


@st.cache_data(show_spinner=False)
def get_datasets():
    return load_datasets()


st.set_page_config(page_title="HW4 - Premier League Story", layout="wide")

datasets = get_datasets()

delta_df = datasets.delta_points.dropna(subset=["delta_points"]).copy()
delta_df = delta_df.sort_values("delta_points", ascending=False)

biggest_riser_row = delta_df.iloc[0]
biggest_faller_row = delta_df.iloc[-1]

st.title("Who rose and who fell from 2023-24 to 2024-25?")
st.write(
    "Was each swing driven more by home form, away form, or both?"
)

teams = sorted(delta_df["Team"].tolist())
selected_team = st.selectbox(
    "Selected team",
    options=teams,
    index=teams.index(str(biggest_riser_row["Team"])),
)

metric_col1, metric_col2 = st.columns(2)
metric_col1.metric(
    "Biggest riser",
    str(biggest_riser_row["Team"]),
    f"{biggest_riser_row['delta_points']:+.0f} points"
)
metric_col2.metric(
    "Biggest faller",
    str(biggest_faller_row["Team"]),
    f"{biggest_faller_row['delta_points']:+.0f} points"
)

st.header("1) What were the biggest swings?")

delta_event = st.altair_chart(
    chart_delta_points(delta_df, selected_team),
    width='stretch',
    on_select="rerun",
    selection_mode=["delta_pick"],
    key="delta_chart",
)

st.header("2) How big was the change?")
p23, p24, p_delta = team_delta(datasets.team_summary, selected_team)
st.write(
    f"{selected_team} moved from **{p23:.0f}** points in 2023-24 to **{p24:.0f}** in 2024-25 "
    f"(**{p_delta:+.0f}**). {movement_sentence(p_delta)}"
)
st.altair_chart(
    chart_points_by_team(datasets.team_summary, selected_team),
    width='stretch',
)

st.header("3) Where did the points come from: home or away?")
driver = home_away_delta(datasets.home_away_points, selected_team)
st.write(
    f"For {selected_team}, home points changed by **{driver['home_change']:+.0f}** "
    f"({driver['home_23']:.0f} to {driver['home_24']:.0f}) and away points changed by "
    f"**{driver['away_change']:+.0f}** ({driver['away_23']:.0f} to {driver['away_24']:.0f}). "
    f"Overall this swing was **{driver['driver']}**."
)
st.altair_chart(
    chart_home_away_points(datasets.home_away_points, selected_team),
    width='stretch',
)

st.markdown("**Max Riser & Max Faller**")
for team in [str(biggest_riser_row["Team"]), str(biggest_faller_row["Team"])]:
    p_driver = home_away_delta(datasets.home_away_points, team)
    st.write(
        f"{team}: total swing **{p_driver['total_change']:+.0f}**. "
        f"Home changed **{p_driver['home_change']:+.0f}**, away changed **{p_driver['away_change']:+.0f}**. "
        f"This profile is {p_driver['driver']}."
    )

st.header("4) What changed at match level?")
st.write(
    "Usage: brush big wins (high GF, low GA), tight games near the diagonal, or heavy losses (low GF, high GA)."
)

scatter_event = st.altair_chart(
    chart_match_scatter(datasets.team_matches, selected_team),
    width='stretch',
    on_select="rerun",
    selection_mode=["match_brush"],
    key="match_scatter",
)

gf = scatter_event.get("selection", {}).get("match_brush", {}).get("GF", [0, 0])
ga = scatter_event.get("selection", {}).get("match_brush", {}).get("GA", [0, 0])
gf_range = (min(float(gf[0]), float(gf[1])), max(float(gf[0]), float(gf[1])))
ga_range = (min(float(ga[0]), float(ga[1])), max(float(ga[0]), float(ga[1])))

selected_matches = datasets.team_matches.loc[datasets.team_matches["Team"] == selected_team].copy()

if gf_range and ga_range:
    selected_matches = selected_matches.loc[
        (selected_matches["GF"] >= gf_range[0])
        & (selected_matches["GF"] <= gf_range[1])
        & (selected_matches["GA"] >= ga_range[0])
        & (selected_matches["GA"] <= ga_range[1])
    ]


st.header("5) Callouts: matches that explain the swing")
callouts = match_callouts(selected_matches, selected_team)
if callouts:
    for line in callouts:
        st.write(f"- {line}")
else:
    st.write("No matches are currently inside the brush. Clear the brush or select a broader region.")

details_cols = ["Date", "season", "Venue", "Opponent", "GF", "GA", "Points", "Referee"]
if selected_matches.empty:
    st.dataframe(pd.DataFrame(columns=details_cols), width='stretch')
else:
    details = selected_matches.sort_values("Date", ascending=True).head(20)[details_cols].copy()
    details["Date"] = details["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(details, width='stretch', hide_index=True)

st.header("6) Self-Exploration")
st.write("Use the interactive views above to test out patterns yourself by doing the following:")
st.write("1. Click a surprising team in the dropdown under the first chart.")
st.write("2. Check whether the swing is home-driven, away-driven, or balanced.")
st.write("3. Brush groups of matches to see which result types drove the shift.")
