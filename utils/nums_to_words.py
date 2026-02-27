"""
Explaining Numbers in Sentences
"""

import pandas as pd


def movement_sentence(delta: float) -> str:
    if delta >= 10:
        return "This was a significant upswing over the previous season."
    if delta >= 5:
        return "This was a moderate upswing over the previous season."
    if delta <= -10:
        return "This was a significant downswing from the previous season."
    if delta <= -5:
        return "This was a moderate downswing from the previous season."
    return "The overall points swing was modest."


def match_callouts(df: pd.DataFrame, team: str) -> list[str]:
    if df.empty:
        return []

    data = df.copy()
    data["abs_gd"] = data["GD"].abs()

    candidates = []
    buckets = [
        data.loc[data["Points"] == 3].sort_values(["GD", "GF", "Date"], ascending=[False, False, True]),
        data.loc[data["Points"] == 0].sort_values(["GD", "GA", "Date"], ascending=[True, False, True]),
        data.loc[(data["GD"].abs() <= 1) & (data["Points"] >= 1)].sort_values("Date", ascending=False),
    ]

    seen = set()
    for bucket in buckets:
        for _, row in bucket.iterrows():
            if row["match_id"] in seen:
                continue
            candidates.append(row.to_dict())
            seen.add(row["match_id"])
            break

    if not candidates:
        candidates = (
            data.sort_values(["abs_gd", "Date"], ascending=[False, True])
            .head(3)
            .to_dict("records")
        )

    lines = []
    for row in candidates[:3]:
        date_str = row["Date"].strftime("%Y-%m-%d")
        venue = row["Venue"]
        opponent = row["Opponent"]
        gf = int(row["GF"])
        ga = int(row["GA"])
        points = int(row["Points"])

        fixture = f"vs {opponent}" if venue == "Home" else f"at {opponent}"
        if points == 3:
            reason = "a high-value win"
        elif points == 1:
            reason = "a tight point"
        else:
            reason = "a costly loss"
        lines.append(f"{date_str}: {team} {gf}-{ga} {fixture} ({venue}) was {reason}.")

    return lines
