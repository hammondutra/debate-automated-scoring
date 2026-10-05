from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class FormatResult:
    team_rankings: pd.DataFrame
    speaker_rankings: pd.DataFrame
    round_results: pd.DataFrame
    reply_rankings: pd.DataFrame = field(default_factory=pd.DataFrame)
    warnings: list[str] = field(default_factory=list)
