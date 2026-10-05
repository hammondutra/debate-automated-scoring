# Contributing

Contributions that make tournament scoring easier to audit, reuse, or adapt are welcome.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Adding a debate format

A new format should:

1. live under `src/debate_scoring/formats/`;
2. validate its required tournament structure;
3. return team rankings, speaker rankings, and round-level results;
4. include sample data;
5. include tests for normal and invalid inputs;
6. document its authoritative scoring source or local tournament rule set.

Avoid silently guessing missing results. If an input is structurally ambiguous, raise a readable validation error.
