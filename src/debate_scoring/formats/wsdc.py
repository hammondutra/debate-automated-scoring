from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from debate_scoring.formats.base import FormatResult
from debate_scoring.schema import clean_common_fields, normalize_columns, require_columns


@dataclass(frozen=True)
class WSDCConfig:
    min_rounds_for_speaker_award: int = 3
    allow_ties: bool = True
    rank_by_average_team_score: bool = True


def _validate_match_structure(df: pd.DataFrame) -> list[str]:
    warnings: list[str] = []
    teams_per_match = df.groupby(["round", "match_id"])["team"].nunique()
    invalid = teams_per_match[teams_per_match != 2]
    if not invalid.empty:
        examples = [f"round {r}, match {m}: {n} teams" for (r, m), n in invalid.head(5).items()]
        raise ValueError("WSDC-style matches require exactly two teams. " + "; ".join(examples))

    normal_scores = df.loc[df["speech_type"] != "reply", "score"]
    if not normal_scores.empty and ((normal_scores < 60) | (normal_scores > 80)).any():
        warnings.append(
            "Some substantive WSDC-style scores fall outside the commonly used 60–80 range. "
            "They were kept because local tournaments may use different scales."
        )

    reply_scores = df.loc[df["speech_type"] == "reply", "score"]
    if not reply_scores.empty and ((reply_scores < 30) | (reply_scores > 40)).any():
        warnings.append(
            "Some reply scores fall outside 30–40 (half of the WSDC substantive scale). "
            "They were kept as entered."
        )

    # Guard against accidental double-counting caused by duplicated ballots or speaker-name typos.
    slot_key = ["round", "match_id", "team", "speech_type", "speaker_position"]
    debaters_per_slot = df.groupby(slot_key)["debater"].nunique()
    conflicting_slots = debaters_per_slot[debaters_per_slot > 1]
    if not conflicting_slots.empty:
        (round_id, match_id, team, speech_type, position), _ = next(
            iter(conflicting_slots.items())
        )
        raise ValueError(
            "A single speech slot is assigned to multiple debaters: "
            f"round {round_id}, match {match_id}, team {team}, "
            f"{speech_type}/{position}."
        )

    if "judge" in df.columns:
        evaluation_key = slot_key + ["judge"]
        duplicate_evaluations = df.duplicated(evaluation_key, keep=False)
        if duplicate_evaluations.any():
            example = df.loc[duplicate_evaluations, evaluation_key].iloc[0].to_dict()
            raise ValueError(
                "Duplicate adjudicator evaluation for the same speech slot: "
                f"{example}. Remove the duplicate row or use a distinct judge identifier."
            )

    speech_counts = (
        df[["round", "match_id", "team", "speech_type", "speaker_position"]]
        .drop_duplicates()
        .groupby(["round", "match_id", "team", "speech_type"])["speaker_position"]
        .nunique()
    )
    unusual_normal = speech_counts.loc[
        speech_counts.index.get_level_values("speech_type") != "reply"
    ]
    if not unusual_normal.empty and (unusual_normal != 3).any():
        warnings.append(
            "At least one team/round does not contain exactly three substantive speech slots. "
            "The run continues because local World Schools-style formats may differ."
        )
    return warnings


def _aggregate_judges(df: pd.DataFrame) -> pd.DataFrame:
    # speaker_position is deliberately part of the key. This preserves iron/double speeches:
    # the same debater can occupy two speech slots in the same round without being collapsed.
    key = ["round", "match_id", "team", "debater", "speech_type", "speaker_position"]
    aggregated = (
        df.groupby(key, as_index=False)
        .agg(
            score=("score", "mean"),
            evaluations=("score", "size"),
            score_std=("score", "std"),
        )
        .fillna({"score_std": 0.0})
    )
    return aggregated


def score_wsdc(df: pd.DataFrame, config: WSDCConfig | None = None) -> FormatResult:
    config = config or WSDCConfig()
    df = normalize_columns(df)
    require_columns(df, ["round", "match_id", "team", "debater", "speaker_position", "score"])

    if "speech_type" not in df.columns:
        df["speech_type"] = "normal"
    if "judge" not in df.columns:
        df["judge"] = "panel"

    df = clean_common_fields(df)
    warnings = _validate_match_structure(df)
    speeches = _aggregate_judges(df)

    team_round = (
        speeches.groupby(["round", "match_id", "team"], as_index=False)
        .agg(team_score=("score", "sum"), speeches=("speaker_position", "count"))
    )

    match_key = ["round", "match_id"]
    team_round["match_max"] = team_round.groupby(match_key)["team_score"].transform("max")
    team_round["is_winner"] = team_round["team_score"].eq(team_round["match_max"])
    team_round["winner_count"] = team_round.groupby(match_key)["is_winner"].transform("sum")

    tied_matches = team_round.loc[team_round["winner_count"] > 1, match_key].drop_duplicates()
    if not tied_matches.empty and not config.allow_ties:
        first = tied_matches.iloc[0]
        raise ValueError(
            f"Tied team totals in round {first['round']}, match {first['match_id']}. "
            "This preset does not allow tied decisions."
        )

    team_round["wins"] = team_round["is_winner"].astype(float) / team_round["winner_count"]
    team_round = team_round.drop(columns=["match_max", "is_winner", "winner_count"])

    team_rankings = (
        team_round.groupby("team", as_index=False)
        .agg(
            wins=("wins", "sum"),
            rounds=("round", "nunique"),
            total_team_score=("team_score", "sum"),
            average_team_score=("team_score", "mean"),
            score_std=("team_score", "std"),
        )
        .fillna({"score_std": 0.0})
    )
    sort_columns = ["wins", "average_team_score", "score_std"]
    ascending = [False, False, True]
    if not config.rank_by_average_team_score:
        sort_columns = ["wins", "total_team_score", "score_std"]
    team_rankings = team_rankings.sort_values(
        sort_columns, ascending=ascending
    ).reset_index(drop=True)
    team_rankings.insert(0, "rank", range(1, len(team_rankings) + 1))

    substantive = speeches[speeches["speech_type"] != "reply"].copy()
    rounds_per_speaker = (
        substantive.groupby("debater", as_index=False)["round"]
        .nunique()
        .rename(columns={"round": "appearances"})
    )
    speaker_rankings = (
        substantive.groupby("debater", as_index=False)
        .agg(
            speeches=("score", "size"),
            average_score=("score", "mean"),
            total_score=("score", "sum"),
            score_std=("score", "std"),
        )
        .fillna({"score_std": 0.0})
        .merge(rounds_per_speaker, on="debater", how="left")
    )

    double_counts = (
        substantive.groupby(["debater", "round"], as_index=False)
        .size()
        .assign(double_speech=lambda x: x["size"].gt(1).astype(int))
        .groupby("debater", as_index=False)["double_speech"]
        .sum()
        .rename(columns={"double_speech": "double_speech_rounds"})
    )
    speaker_rankings = speaker_rankings.merge(double_counts, on="debater", how="left")
    speaker_rankings["eligible"] = (
        speaker_rankings["appearances"] >= config.min_rounds_for_speaker_award
    )
    speaker_rankings = speaker_rankings.sort_values(
        ["eligible", "average_score", "total_score", "debater"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    speaker_rankings.insert(0, "rank", range(1, len(speaker_rankings) + 1))

    replies = speeches[speeches["speech_type"] == "reply"].copy()
    if replies.empty:
        reply_rankings = pd.DataFrame(
            columns=[
                "rank",
                "debater",
                "reply_speeches",
                "average_reply_score",
                "total_reply_score",
            ]
        )
    else:
        reply_rankings = (
            replies.groupby("debater", as_index=False)
            .agg(
                reply_speeches=("score", "size"),
                average_reply_score=("score", "mean"),
                total_reply_score=("score", "sum"),
            )
            .sort_values(
                ["average_reply_score", "total_reply_score", "debater"],
                ascending=[False, False, True],
            )
            .reset_index(drop=True)
        )
        reply_rankings.insert(0, "rank", range(1, len(reply_rankings) + 1))

    round_results = team_round.sort_values(
        ["round", "match_id", "wins", "team_score"],
        ascending=[True, True, False, False],
    )
    return FormatResult(
        team_rankings=team_rankings,
        speaker_rankings=speaker_rankings,
        round_results=round_results.reset_index(drop=True),
        reply_rankings=reply_rankings,
        warnings=warnings,
    )
