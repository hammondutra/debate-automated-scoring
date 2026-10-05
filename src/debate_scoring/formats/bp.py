from __future__ import annotations

import pandas as pd

from debate_scoring.formats.base import FormatResult
from debate_scoring.schema import clean_common_fields, normalize_columns, require_columns

TEAM_POINTS = {1: 3, 2: 2, 3: 1, 4: 0}


def score_bp(df: pd.DataFrame) -> FormatResult:
    """Score British Parliamentary / WUDC-style finalized ballots.

    The input represents the finalized panel outcome: each team has a placement (1–4), and
    each speaker has a speaker score. Team points are derived as 3/2/1/0.
    """
    df = normalize_columns(df)
    require_columns(
        df,
        ["round", "match_id", "team", "debater", "speaker_position", "score", "placement"],
    )
    df = clean_common_fields(df)
    warnings: list[str] = []

    teams_per_match = df.groupby(["round", "match_id"])["team"].nunique()
    invalid_teams = teams_per_match[teams_per_match != 4]
    if not invalid_teams.empty:
        examples = [
            f"round {r}, match {m}: {n} teams"
            for (r, m), n in invalid_teams.head(5).items()
        ]
        raise ValueError("BP matches require exactly four teams. " + "; ".join(examples))

    for (round_id, match_id), group in df.groupby(["round", "match_id"]):
        placement_by_team = group[["team", "placement"]].drop_duplicates()
        if placement_by_team["team"].duplicated().any():
            raise ValueError(
                f"A team has multiple placements in round {round_id}, match {match_id}."
            )
        if sorted(placement_by_team["placement"].tolist()) != [1, 2, 3, 4]:
            raise ValueError(
                f"Round {round_id}, match {match_id} must contain placements 1, 2, 3, "
                "and 4 exactly once."
            )

    if ((df["score"] < 50) | (df["score"] > 100)).any():
        warnings.append(
            "Some BP speaker scores fall outside the WUDC 50–100 speaker scale. "
            "They were kept because local tournaments may use customized scales."
        )

    speeches_per_team = df.groupby(["round", "match_id", "team"])[
        "speaker_position"
    ].nunique()
    invalid_speech_counts = speeches_per_team[speeches_per_team != 2]
    if not invalid_speech_counts.empty:
        (round_id, match_id, team), count = next(iter(invalid_speech_counts.items()))
        raise ValueError(
            "BP teams require exactly two finalized speech slots. "
            f"Round {round_id}, match {match_id}, team {team} has {count}."
        )

    duplicate_slots = df.duplicated(
        ["round", "match_id", "team", "speaker_position"], keep=False
    )
    if duplicate_slots.any():
        examples = df.loc[
            duplicate_slots, ["round", "match_id", "team", "speaker_position"]
        ].head(5)
        raise ValueError(
            "BP input should contain one finalized score per team speech slot. "
            "Duplicate slots found: "
            + examples.to_dict(orient="records").__repr__()
        )

    team_round = (
        df.groupby(["round", "match_id", "team", "placement"], as_index=False)
        .agg(team_speaker_points=("score", "sum"), speeches=("speaker_position", "size"))
    )
    team_round["team_points"] = team_round["placement"].map(TEAM_POINTS)

    for (round_id, match_id), group in team_round.groupby(["round", "match_id"]):
        ordered = group.sort_values("placement")
        totals = ordered["team_speaker_points"].tolist()
        if not all(left > right for left, right in zip(totals, totals[1:], strict=False)):
            raise ValueError(
                f"In round {round_id}, match {match_id}, combined speaker points must strictly "
                "decrease from 1st to 4th to match the finalized team ranking."
            )

    team_rankings = (
        team_round.groupby("team", as_index=False)
        .agg(
            team_points=("team_points", "sum"),
            total_speaker_points=("team_speaker_points", "sum"),
            rounds=("round", "nunique"),
            average_speaker_points=("team_speaker_points", "mean"),
        )
        .sort_values(
            ["team_points", "total_speaker_points", "average_speaker_points", "team"],
            ascending=[False, False, False, True],
        )
        .reset_index(drop=True)
    )
    team_rankings.insert(0, "rank", range(1, len(team_rankings) + 1))

    speaker_rankings = (
        df.groupby("debater", as_index=False)
        .agg(
            speeches=("score", "size"),
            total_score=("score", "sum"),
            average_score=("score", "mean"),
            score_std=("score", "std"),
        )
        .fillna({"score_std": 0.0})
        .sort_values(
            ["total_score", "average_score", "debater"],
            ascending=[False, False, True],
        )
        .reset_index(drop=True)
    )
    speaker_rankings.insert(0, "rank", range(1, len(speaker_rankings) + 1))

    round_results = team_round.sort_values(
        ["round", "match_id", "placement"]
    ).reset_index(drop=True)
    return FormatResult(
        team_rankings=team_rankings,
        speaker_rankings=speaker_rankings,
        round_results=round_results,
        warnings=warnings,
    )
