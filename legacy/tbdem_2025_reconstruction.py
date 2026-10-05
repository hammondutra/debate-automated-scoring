"""Compact reconstruction of the earlier TBDEM ranking workflow.

Preserved for project-history traceability. The production implementation lives under
``src/debate_scoring`` and adds validation, multiple-judge aggregation by speech slot,
separate substantive/reply rankings, exports, tests, and format abstraction.
"""

import pandas as pd


def assign_wins(group: pd.DataFrame) -> pd.DataFrame:
    max_score = group["team_score"].max()
    winners = group["team_score"] == max_score

    if winners.sum() == 1:
        group["Win"] = winners.astype(int)
    else:
        group["Win"] = winners.astype(float) * 0.5

    return group


def legacy_rank(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed = data.groupby(
        ["Round", "Match_ID", "Team", "Debater", "Speech_Type"],
        as_index=False,
    )["Score"].max()

    appearances = (
        processed.groupby("Debater")["Round"]
        .nunique()
        .reset_index()
        .rename(columns={"Round": "Appearances"})
    )
    speakers = (
        processed.groupby("Debater")
        .agg(total_speeches=("Score", "count"), average_score=("Score", "mean"))
        .reset_index()
        .merge(appearances, on="Debater", how="left")
    )
    speakers["Eligible"] = speakers["Appearances"] >= 3
    speakers = speakers.sort_values(["Eligible", "average_score"], ascending=[False, False])

    replies = (
        processed[processed["Speech_Type"] == "reply"]
        .groupby("Debater")["Score"]
        .mean()
        .reset_index()
        .rename(columns={"Score": "average_reply_score"})
        .sort_values("average_reply_score", ascending=False)
    )

    team_round = (
        processed.groupby(["Round", "Match_ID", "Team"], as_index=False)
        .agg(team_score=("Score", "sum"))
        .groupby(["Round", "Match_ID"], group_keys=False)
        .apply(assign_wins)
        .reset_index(drop=True)
    )
    teams = (
        team_round.groupby("Team")
        .agg(
            wins=("Win", "sum"),
            average_team_score=("team_score", "mean"),
            std_team_score=("team_score", "std"),
        )
        .reset_index()
        .fillna({"std_team_score": 0})
        .sort_values(
            ["wins", "average_team_score", "std_team_score"],
            ascending=[False, False, True],
        )
    )
    return teams, speakers, replies
