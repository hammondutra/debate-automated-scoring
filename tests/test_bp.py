import pandas as pd
import pytest

from debate_scoring.engine import run_tournament


def _valid_bp_data():
    return pd.DataFrame(
        [
            [1, "M1", "A", "A1", "PM", 1, 82],
            [1, "M1", "A", "A2", "DPM", 1, 82],
            [1, "M1", "B", "B1", "LO", 2, 80],
            [1, "M1", "B", "B2", "DLO", 2, 80],
            [1, "M1", "C", "C1", "MG", 3, 77],
            [1, "M1", "C", "C2", "GW", 3, 77],
            [1, "M1", "D", "D1", "MO", 4, 75],
            [1, "M1", "D", "D2", "OW", 4, 75],
        ],
        columns=[
            "round",
            "match_id",
            "team",
            "debater",
            "speaker_position",
            "placement",
            "score",
        ],
    )


def test_bp_assigns_standard_team_points():
    result = run_tournament(_valid_bp_data(), "wudc")
    points = result.round_results.set_index("team")["team_points"].to_dict()
    assert points == {"A": 3, "B": 2, "C": 1, "D": 0}
    assert result.team_rankings.iloc[0]["team"] == "A"


def test_bp_rejects_speaker_points_incompatible_with_placement():
    df = _valid_bp_data()
    df.loc[df["team"] == "D", "score"] = 90
    with pytest.raises(ValueError, match="must strictly decrease"):
        run_tournament(df, "wudc")
