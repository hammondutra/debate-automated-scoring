from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from debate_scoring.formats.bp import score_bp
from debate_scoring.formats.wsdc import WSDCConfig, score_wsdc


@dataclass
class TournamentResult:
    format_name: str
    team_rankings: pd.DataFrame
    speaker_rankings: pd.DataFrame
    round_results: pd.DataFrame
    reply_rankings: pd.DataFrame
    warnings: list[str]


def run_tournament(df: pd.DataFrame, format_name: str) -> TournamentResult:
    requested = format_name.strip().lower()

    if requested in {"tbdem", "tbderm"}:
        result = score_wsdc(
            df,
            WSDCConfig(min_rounds_for_speaker_award=3, allow_ties=True),
        )
        label = "TBDEM / World Schools-style"
    elif requested in {"wsdc", "world_schools"}:
        result = score_wsdc(
            df,
            WSDCConfig(min_rounds_for_speaker_award=3, allow_ties=False),
        )
        label = "World Schools-style (strict decisions)"
    elif requested in {"bp", "wudc", "british_parliamentary"}:
        result = score_bp(df)
        label = "WUDC / British Parliamentary"
    else:
        raise ValueError(
            f"Unsupported format '{format_name}'. Choose one of: tbdem, wsdc, bp, wudc."
        )

    return TournamentResult(
        format_name=label,
        team_rankings=result.team_rankings,
        speaker_rankings=result.speaker_rankings,
        round_results=result.round_results,
        reply_rankings=result.reply_rankings,
        warnings=result.warnings,
    )
