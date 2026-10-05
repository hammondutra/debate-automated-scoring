.PHONY: install dev test lint app sample

install:
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

app:
	streamlit run app.py

sample:
	mkdir -p results
	debate-scoring rank data/sample_tbdem.csv --format tbdem --output results/tbdem.xlsx
	debate-scoring rank data/sample_wudc.csv --format wudc --output results/wudc.xlsx
