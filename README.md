# Debate Automated Scoring

A reusable scoring and ranking toolkit for debate tournaments, built from the workflow used to automate tabulation at the **Torneio Brasileiro de Debates do Ensino Médio (TBDEM)**, Brazil's national high-school debate championship.

The original workflow processed tournament-scale data — roughly **500 debaters and 3,000 round-level evaluations** — while accounting for speaker order, reply speeches, multiple adjudicators, and double-speech/iron cases. Automating the ranking pipeline reduced manual processing by approximately **12.5 hours per cycle**.

This repository turns that workflow into a reproducible tool that tournament organizers can run from either a command line or a simple browser interface.

## What it supports

- **TBDEM / World Schools-style tournaments**
  - multiple adjudicator scores per speech
  - automatic score aggregation
  - team and individual rankings
  - separate reply-speech rankings
  - minimum-round eligibility rules
  - double-speech / iron-person cases without collapsing distinct speech slots
  - configurable handling of exact team-score ties
- **British Parliamentary / WUDC-style tournaments**
  - four-team rooms
  - 1st–4th placements
  - automatic 3/2/1/0 team points
  - speaker-point aggregation
  - validation that speaker-point totals are compatible with room placements
- CSV and Excel input
- English and common Portuguese column names
- Excel result exports
- automated validation with readable error messages
- command-line and no-code Streamlit interfaces
- unit tests and continuous integration

The project deliberately focuses on **scoring, validation, ranking, and reproducible outputs** rather than trying to replace full tournament-management platforms.

## Quick start

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Run the browser interface

```bash
streamlit run app.py
```

Download the template for your format, fill it with tournament results, upload it, and export the generated rankings workbook.

### 3. Or use the command line

Create a template:

```bash
debate-scoring template --format tbdem --output tournament.csv
```

Validate it:

```bash
debate-scoring validate tournament.csv --format tbdem
```

Generate rankings:

```bash
debate-scoring rank tournament.csv --format tbdem --output results.xlsx
```

For British Parliamentary tournaments, replace `tbdem` with `wudc`.

## Example data

Ready-to-run examples are included in [`data/`](data/):

- `sample_tbdem.csv`
- `sample_wudc.csv`
- `template_tbdem.csv`
- `template_wudc.csv`

Try them immediately:

```bash
debate-scoring rank data/sample_tbdem.csv --format tbdem --output results/tbdem.xlsx
debate-scoring rank data/sample_wudc.csv --format wudc --output results/wudc.xlsx
```

## Architecture

The scoring logic is separated from file handling and the user interface:

```text
src/debate_scoring/
├── engine.py          # format selection and public API
├── io.py              # CSV/Excel input and result exports
├── schema.py          # normalization and validation helpers
└── formats/
    ├── wsdc.py        # TBDEM / World Schools-style scoring
    └── bp.py          # British Parliamentary / WUDC scoring
```

That separation makes it possible to add another debate format without rewriting the interface or export pipeline.

## Reproducibility and validation

Every run follows the same pipeline:

1. normalize input columns;
2. validate the tournament structure;
3. aggregate adjudicator-level records where appropriate;
4. calculate round results;
5. calculate team and speaker rankings;
6. export an auditable workbook.

Invalid structures — such as a BP room without four distinct placements — stop with an explicit error rather than silently producing a ranking.

The format-specific assumptions and source references are documented in [`docs/SCORING_RULES.md`](docs/SCORING_RULES.md). Input schemas are documented in [`docs/DATA_FORMAT.md`](docs/DATA_FORMAT.md).

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run static checks:

```bash
ruff check .
```

## License

MIT — see [`LICENSE`](LICENSE).
