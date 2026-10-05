from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from debate_scoring.engine import TournamentResult


def load_dataframe(source: str | Path | BinaryIO, filename: str | None = None) -> pd.DataFrame:
    suffix = Path(filename or str(source)).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(source)
    raise ValueError("Input must be a .csv, .xlsx, or .xls file.")


def export_excel(result: TournamentResult) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        result.team_rankings.to_excel(writer, sheet_name="team_rankings", index=False)
        result.speaker_rankings.to_excel(writer, sheet_name="speaker_rankings", index=False)
        result.round_results.to_excel(writer, sheet_name="round_results", index=False)
        if not result.reply_rankings.empty:
            result.reply_rankings.to_excel(writer, sheet_name="reply_rankings", index=False)
        pd.DataFrame(
            {
                "field": ["format", "warnings"],
                "value": [result.format_name, " | ".join(result.warnings) or "None"],
            }
        ).to_excel(writer, sheet_name="run_info", index=False)
    return buffer.getvalue()


def template_dataframe(format_name: str) -> pd.DataFrame:
    name = format_name.strip().lower()
    if name in {"wsdc", "tbdem", "tbderm", "world_schools"}:
        return pd.DataFrame(
            columns=[
                "round",
                "match_id",
                "team",
                "debater",
                "speech_type",
                "speaker_position",
                "judge",
                "score",
            ]
        )
    if name in {"bp", "wudc", "british_parliamentary"}:
        return pd.DataFrame(
            columns=[
                "round",
                "match_id",
                "team",
                "debater",
                "speaker_position",
                "placement",
                "score",
            ]
        )
    raise ValueError("Unknown format. Choose wsdc/tbdem or bp/wudc.")
