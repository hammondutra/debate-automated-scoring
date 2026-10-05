from __future__ import annotations

import argparse
from pathlib import Path

from debate_scoring.engine import run_tournament
from debate_scoring.io import export_excel, load_dataframe, template_dataframe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="debate-scoring",
        description="Validate, score, and rank debate tournament data.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    template = subparsers.add_parser("template", help="Create an empty CSV template.")
    template.add_argument("--format", required=True, choices=["tbdem", "wsdc", "bp", "wudc"])
    template.add_argument("--output", required=True)

    validate = subparsers.add_parser("validate", help="Validate a tournament dataset.")
    validate.add_argument("input")
    validate.add_argument("--format", required=True, choices=["tbdem", "wsdc", "bp", "wudc"])

    rank = subparsers.add_parser("rank", help="Calculate rankings and export an Excel workbook.")
    rank.add_argument("input")
    rank.add_argument("--format", required=True, choices=["tbdem", "wsdc", "bp", "wudc"])
    rank.add_argument("--output", required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "template":
        template_dataframe(args.format).to_csv(args.output, index=False)
        print(f"Template written to {args.output}")
        return

    df = load_dataframe(args.input)
    result = run_tournament(df, args.format)

    if args.command == "validate":
        print(f"Valid {result.format_name} dataset.")
        for warning in result.warnings:
            print(f"Warning: {warning}")
        return

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(export_excel(result))
    print(f"Rankings written to {output}")
    for warning in result.warnings:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    main()
