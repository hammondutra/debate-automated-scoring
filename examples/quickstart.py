from pathlib import Path

from debate_scoring.engine import run_tournament
from debate_scoring.io import export_excel, load_dataframe

input_file = Path("data/sample_tbdem.csv")
output_file = Path("results/example.xlsx")
output_file.parent.mkdir(exist_ok=True)

results = run_tournament(load_dataframe(input_file), "tbdem")
output_file.write_bytes(export_excel(results))

print(results.team_rankings.head())
print(results.speaker_rankings.head())
print(f"Saved: {output_file}")
