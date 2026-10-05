import pandas as pd
import pytest

from debate_scoring.engine import run_tournament


def test_wsdc_averages_judges_and_preserves_double_speech():
    rows = [
        [1, "M1", "A", "Ana", "normal", "1", "J1", 70],
        [1, "M1", "A", "Ana", "normal", "1", "J2", 72],
        [1, "M1", "A", "Ana", "normal", "3", "J1", 74],
        [1, "M1", "A", "Ana", "normal", "3", "J2", 76],
        [1, "M1", "A", "Bia", "normal", "2", "J1", 73],
        [1, "M1", "A", "Bia", "normal", "2", "J2", 73],
        [1, "M1", "A", "Bia", "reply", "reply", "J1", 36],
        [1, "M1", "A", "Bia", "reply", "reply", "J2", 36],
        [1, "M1", "B", "Caio", "normal", "1", "J1", 70],
        [1, "M1", "B", "Caio", "normal", "1", "J2", 70],
        [1, "M1", "B", "Duda", "normal", "2", "J1", 70],
        [1, "M1", "B", "Duda", "normal", "2", "J2", 70],
        [1, "M1", "B", "Eli", "normal", "3", "J1", 70],
        [1, "M1", "B", "Eli", "normal", "3", "J2", 70],
        [1, "M1", "B", "Caio", "reply", "reply", "J1", 35],
        [1, "M1", "B", "Caio", "reply", "reply", "J2", 35],
    ]
    df = pd.DataFrame(
        rows,
        columns=[
            "round",
            "match_id",
            "team",
            "debater",
            "speech_type",
            "speaker_position",
            "judge",
            "score",
        ],
    )

    result = run_tournament(df, "tbdem")
    ana = result.speaker_rankings.set_index("debater").loc["Ana"]
    assert ana["speeches"] == 2
    assert ana["average_score"] == pytest.approx(73.0)
    assert ana["double_speech_rounds"] == 1

    # Reply scores are deliberately not mixed into the substantive speaker average.
    bia = result.speaker_rankings.set_index("debater").loc["Bia"]
    assert bia["average_score"] == pytest.approx(73.0)

    winner = result.team_rankings.iloc[0]
    assert winner["team"] == "A"
    assert winner["wins"] == pytest.approx(1.0)


def test_wsdc_accepts_portuguese_headers():
    df = pd.DataFrame(
        {
            "rodada": [1] * 6,
            "sala": ["M1"] * 6,
            "equipe": ["A", "A", "A", "B", "B", "B"],
            "debatedor": ["A1", "A2", "A3", "B1", "B2", "B3"],
            "posição": [1, 2, 3, 1, 2, 3],
            "nota": [74, 74, 74, 70, 70, 70],
        }
    )
    result = run_tournament(df, "tbdem")
    assert result.team_rankings.iloc[0]["team"] == "A"


def test_strict_wsdc_rejects_tied_team_total():
    df = pd.DataFrame(
        {
            "round": [1] * 6,
            "match_id": ["M1"] * 6,
            "team": ["A", "A", "A", "B", "B", "B"],
            "debater": ["A1", "A2", "A3", "B1", "B2", "B3"],
            "speaker_position": [1, 2, 3, 1, 2, 3],
            "score": [70, 70, 70, 70, 70, 70],
        }
    )
    with pytest.raises(ValueError, match="Tied team totals"):
        run_tournament(df, "wsdc")
