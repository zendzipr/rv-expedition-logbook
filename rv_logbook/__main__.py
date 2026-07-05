from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .importers import CsvImportError, import_csv, write_json
from .merge import MergeError, merge_record_files
from .render import BinderRenderError, fail, load_json, render_binder
from .render_html import render_html
from .schema import SchemaValidationError, validate_file, validate_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rv_logbook", description="RV Expedition Logbook tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="render a Markdown binder from trip JSON")
    render_parser.add_argument("input", help="input trip JSON file")
    render_parser.add_argument("output", help="output Markdown file")

    render_html_parser = subparsers.add_parser("render-html", help="render an HTML trip report from trip JSON")
    render_html_parser.add_argument("input", help="input trip JSON file")
    render_html_parser.add_argument("output", help="output HTML file")

    validate_parser = subparsers.add_parser("validate", help="validate a JSON file against a project schema")
    validate_parser.add_argument("input", help="input JSON file")
    validate_parser.add_argument("--schema", default="trip", help="schema name, e.g. trip, travel-day, campground")

    import_parser = subparsers.add_parser("import-csv", help="import a supported CSV file into normalized JSON")
    import_parser.add_argument("csv_type", choices=["fuel-stop", "expense"], help="CSV import type")
    import_parser.add_argument("input", help="input CSV file")
    import_parser.add_argument("output", help="output JSON file")

    merge_parser = subparsers.add_parser("merge-records", help="merge normalized records into a trip JSON file")
    merge_parser.add_argument("record_type", choices=["fuel-stop", "expense"], help="record type to merge")
    merge_parser.add_argument("trip", help="trip JSON file")
    merge_parser.add_argument("records", help="records JSON array file")
    merge_parser.add_argument("output", help="output merged trip JSON file")
    merge_parser.add_argument("--mode", choices=["append", "replace"], default="append", help="append new records or replace existing records for each matching travel day")

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


def render_html_command(input_path: str, output_path: str) -> int:
    trip = load_json(Path(input_path))
    try:
        rendered = render_html(trip)
    except BinderRenderError as exc:
        fail(str(exc))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    print(f"Rendered HTML report: {destination}")
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


def merge_records_command(record_type: str, trip_path: str, records_path: str, output_path: str, mode: str = "append") -> int:
    try:
        merge_record_files(record_type, Path(trip_path), Path(records_path), Path(output_path), mode=mode)
    except MergeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Merged {record_type} records into {output_path} using {mode} mode")
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
    if args.command == "render-html":
        return render_html_command(args.input, args.output)
    if args.command == "validate":
        return validate_command(args.input, args.schema)
    if args.command == "import-csv":
        return import_csv_command(args.csv_type, args.input, args.output)
    if args.command == "merge-records":
        return merge_records_command(args.record_type, args.trip, args.records, args.output, args.mode)
    if args.command == "validate-repo":
        return validate_repo_command()
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
