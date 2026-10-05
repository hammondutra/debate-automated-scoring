# Data format

The project uses a row-oriented format so that tournament data can be created in Excel, Google Sheets, LibreOffice, or any system that exports CSV/XLSX.

## TBDEM / World Schools-style input

Required columns:

| Column | Meaning |
|---|---|
| `round` | Round identifier |
| `match_id` | Debate/room identifier within the round |
| `team` | Team name or code |
| `debater` | Speaker name or stable ID |
| `speaker_position` | Distinct speech slot, e.g. `1`, `2`, `3`, `reply` |
| `score` | Score assigned by one adjudicator |

Optional columns:

| Column | Meaning |
|---|---|
| `speech_type` | `normal` or `reply`; defaults to `normal` |
| `judge` | Judge/adjudicator identifier; defaults to `panel` |

### Multiple adjudicators

Enter one row per adjudicator score. For example, if three judges score the same first speech, use three rows with the same round, match, team, debater, speech type, and speaker position, but different `judge` values.

The engine averages those scores before calculating team totals.

### Double speeches / iron-person cases

Do **not** duplicate the same `speaker_position`. Instead, enter the same debater in each distinct speech slot they delivered.

Example:

```csv
round,match_id,team,debater,speech_type,speaker_position,judge,score
4,M1,Equipe Azul,Ana,normal,1,J1,74
4,M1,Equipe Azul,Ana,normal,3,J1,75
```

Because the speech position is part of the aggregation key, both speeches are preserved.

## British Parliamentary / WUDC-style input

Required columns:

| Column | Meaning |
|---|---|
| `round` | Round identifier |
| `match_id` | Room/debate identifier |
| `team` | Team name or code |
| `debater` | Speaker name or stable ID |
| `speaker_position` | Speaker slot, e.g. `PM`, `DPM`, `LO`, `DLO`, `MG`, `GW`, `MO`, `OW` |
| `placement` | Finalized team placement: 1, 2, 3, or 4 |
| `score` | Finalized speaker score |

The BP/WUDC input is intentionally modeled as the **finalized panel ballot**, not as separate preliminary scores from each judge. This mirrors the format's consensus-based allocation of placements and speaker scores.

## Portuguese column aliases

The loader accepts common Portuguese names and automatically maps them to the canonical schema. Examples include:

| Portuguese | Canonical |
|---|---|
| `rodada` | `round` |
| `sala`, `confronto` | `match_id` |
| `equipe`, `time` | `team` |
| `debatedor`, `orador` | `debater` |
| `tipo_discurso` | `speech_type` |
| `posição`, `posicao`, `ordem` | `speaker_position` |
| `juiz`, `adjudicador` | `judge` |
| `nota`, `pontuacao` | `score` |
| `colocação`, `colocacao` | `placement` |

## Templates

Create an empty template without opening the source code:

```bash
debate-scoring template --format tbdem --output tbdem.csv
debate-scoring template --format wudc --output wudc.csv
```
