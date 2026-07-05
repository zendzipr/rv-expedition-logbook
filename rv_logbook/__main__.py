from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .importers import CsvImportError, import_csv, write_json
from .render import BinderRenderError, fail, load_json, render_binder
from .schema import SchemaValidationError, validate_file, validate_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rv_logbook", description="RV Expedition Logbook tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="render a Markdown binder from trip JSON")
    render_parser.add_argument("input", help="input trip JSON file")
    render_parser.add_argument("output", help="output Markdown file")

    validate_parser = subparsers.add_parser("validate", help="validate a JSON file against a project schema")
    validate_parser.add_argument("input", help="input JSON file")
    validate_parser.add_argument("--schema", default="trip", help="schema name, e.g. trip, travel-day, campground")

    import_parser = subparsers.add_parser("import-csv", help="import a supported CSV file into normalized JSON")
    import_parser.add_argument("csv_type", choices=["fuel-stop", "expense"], help="CSV import type")
    import_parser.add_argument("input", help="input CSV file")
    import_parser.add_argument("output", help="output JSON file")

    subparsers.add_parser("validate-repo", help="validate repository schemas and examples")
    return parser


def render_command(input_path: str, output_path: str) -> int:
    trip = load_json(Path(input_path))
    try:
        rendered = render_binder(trip)
    except BinderRenderError as exc:
        fail(str(exc))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    print(f"Rendered binder: {destination}")
    return 0


def validate_command(input_path: str, schema_name: str) -> int:
    try:
        validate_file(Path(input_path), schema_name)
    except SchemaValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Valid: {input_path} matches {schema_name}")
    return 0


def import_csv_command(csv_type: str, input_path: str, output_path: str) -> int:
    try:
        records = import_csv(csv_type, Path(input_path))
    except CsvImportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    destination = Path(output_path)
    write_json(records, destination)
    print(f"Imported {len(records)} {csv_type} records to {destination}")
    return 0


def validate_repo_command() -> int:
    try:
        checked = validate_repository()
    except SchemaValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for item in checked:
        print(f"OK schema: {item}")
    print("Repository validation complete.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "render":
        return render_command(args.input, args.output)
    if args.command == "validate":
        return validate_command(args.input, args.schema)
    if args.command == "import-csv":
        return import_csv_command(args.csv_type, args.input, args.output)
    if args.command == "validate-repo":
        return validate_repo_command()
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
