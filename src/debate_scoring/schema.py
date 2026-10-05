from __future__ import annotations

import re
from collections.abc import Iterable

import pandas as pd

COLUMN_ALIASES = {
    "round": "round",
    "rodada": "round",
    "match_id": "match_id",
    "match": "match_id",
    "debate_id": "match_id",
    "debate": "match_id",
    "room": "match_id",
    "sala": "match_id",
    "confronto": "match_id",
    "team": "team",
    "equipe": "team",
    "time": "team",
    "debater": "debater",
    "speaker": "debater",
    "debatedor": "debater",
    "orador": "debater",
    "speech_type": "speech_type",
    "speech": "speech_type",
    "tipo_discurso": "speech_type",
    "tipo_de_discurso": "speech_type",
    "speaker_position": "speaker_position",
    "position": "speaker_position",
    "ordem": "speaker_position",
    "posicao": "speaker_position",
    "posição": "speaker_position",
    "judge": "judge",
    "adjudicator": "judge",
    "juiz": "judge",
    "adjudicador": "judge",
    "score": "score",
    "nota": "score",
    "pontuacao": "score",
    "placement": "placement",
    "rank": "placement",
    "colocacao": "placement",
    "colocação": "placement",
}

SPEECH_TYPE_ALIASES = {
    "normal": "normal",
    "regular": "normal",
    "substantive": "normal",
    "principal": "normal",
    "reply": "reply",
    "resposta": "reply",
    "réplica": "reply",
    "replica": "reply",
}


def _slug(value: object) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[\s\-/]+", "_", text)
    return re.sub(r"[^\wÀ-ÿ]", "", text)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common English and Portuguese tournament column names."""
    renamed = {}
    for column in df.columns:
        slug = _slug(column)
        renamed[column] = COLUMN_ALIASES.get(slug, slug)

    result = df.rename(columns=renamed).copy()
    duplicated = result.columns[result.columns.duplicated()].tolist()
    if duplicated:
        raise ValueError(f"Multiple input columns map to the same field: {duplicated}")

    if "speech_type" in result.columns:
        result["speech_type"] = (
            result["speech_type"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(lambda value: SPEECH_TYPE_ALIASES.get(value, value))
        )
    return result


def require_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
            + ". See docs/DATA_FORMAT.md or generate a template with the CLI."
        )


def clean_common_fields(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in ["round", "match_id", "team", "debater", "speaker_position", "judge"]:
        if column in result.columns:
            result[column] = result[column].astype(str).str.strip()
    if "score" in result.columns:
        result["score"] = pd.to_numeric(result["score"], errors="raise")
    if "placement" in result.columns:
        result["placement"] = pd.to_numeric(result["placement"], errors="raise").astype(int)
    return result
