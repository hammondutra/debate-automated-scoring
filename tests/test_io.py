from io import BytesIO

import pandas as pd

from debate_scoring.engine import run_tournament
from debate_scoring.io import export_excel


def test_excel_export_contains_rankings():
    df = pd.DataFrame(
        {
            "round": [1] * 6,
            "match_id": ["M1"] * 6,
            "team": ["A", "A", "A", "B", "B", "B"],
            "debater": ["A1", "A2", "A3", "B1", "B2", "B3"],
            "speaker_position": [1, 2, 3, 1, 2, 3],
            "score": [74, 74, 74, 70, 70, 70],
        }
    )
    result = run_tournament(df, "tbdem")
    payload = export_excel(result)
    workbook = pd.ExcelFile(BytesIO(payload))
    assert "team_rankings" in workbook.sheet_names
    assert "speaker_rankings" in workbook.sheet_names
    assert "round_results" in workbook.sheet_names
