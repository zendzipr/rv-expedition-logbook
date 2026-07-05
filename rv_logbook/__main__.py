from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .importers import CsvImportError, import_csv, write_json
from .live_trip import (
    LiveTripError,
    add_campground_review,
    add_daily_review,
    add_final_reflection,
    add_fuel_stop,
    add_meal,
    add_mileage_note,
    add_stop,
    add_travel_day_note,
    add_trip_entry,
    add_trip_note,
    create_live_trip,
    export_trip_bundle,
    finalize_trip,
    follow_up_questions,
    render_current_binder,
    render_current_binder_html,
    render_final_binder_html,
    trip_capture_prompts,
    trip_checklist,
    trip_daily_summary,
)
from .merge import MergeError, merge_record_files
from .render import BinderRenderError, fail, load_json, render_binder
from .render_html import render_html
from .rv_trip_wizard import RvTripWizardImportError, import_rtw_file
from .schema import SchemaValidationError, validate_file, validate_repository
from .workflows import WorkflowError, ingest_csv_to_trip


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rv_logbook", description="RV Expedition Logbook tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="render a Markdown binder from trip JSON")
    render_parser.add_argument("input", help="input trip JSON file")
    render_parser.add_argument("output", help="output Markdown file")

    create_live_parser = subparsers.add_parser("create-live-trip", help="create a live trip workspace from an RV Trip Wizard export")
    create_live_parser.add_argument("trip_slug", help="folder slug for the trip workspace")
    create_live_parser.add_argument("rtw_input", help="input RV Trip Wizard export JSON file")
    create_live_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_note_parser = subparsers.add_parser("add-trip-note", help="append a typed note to a live trip workspace")
    add_note_parser.add_argument("trip_slug", help="trip workspace slug")
    add_note_parser.add_argument("note_type", choices=["daily", "campground", "meal", "travel", "stop", "general"], help="note category")
    add_note_parser.add_argument("content", help="note text to append")
    add_note_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_entry_parser = subparsers.add_parser("add-trip-entry", help="store a structured live trip entry in the trip database")
    add_entry_parser.add_argument("trip_slug", help="trip workspace slug")
    add_entry_parser.add_argument("entry_type", choices=["meal", "stop", "campground", "travel", "fuel", "mileage", "general"], help="structured entry category")
    add_entry_parser.add_argument("title", help="short entry title")
    add_entry_parser.add_argument("content", help="entry details")
    add_entry_parser.add_argument("--date", dest="occurred_on", help="optional entry date in YYYY-MM-DD form")
    add_entry_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_entry_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_meal_parser = subparsers.add_parser("add-meal", help="capture a meal in binder-friendly form")
    add_meal_parser.add_argument("trip_slug", help="trip workspace slug")
    add_meal_parser.add_argument("restaurant", help="meal title or restaurant name")
    add_meal_parser.add_argument("location", help="meal location")
    add_meal_parser.add_argument("notes", help="meal notes")
    add_meal_parser.add_argument("--date", dest="occurred_on", help="optional meal date in YYYY-MM-DD form")
    add_meal_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_meal_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_fuel_parser = subparsers.add_parser("add-fuel-stop", help="capture a fuel stop in binder-friendly form")
    add_fuel_parser.add_argument("trip_slug", help="trip workspace slug")
    add_fuel_parser.add_argument("vendor", help="fuel vendor")
    add_fuel_parser.add_argument("location", help="fuel stop location")
    add_fuel_parser.add_argument("gallons", help="gallons pumped")
    add_fuel_parser.add_argument("total_cost", help="total fuel cost")
    add_fuel_parser.add_argument("odometer", help="odometer reading")
    add_fuel_parser.add_argument("--date", dest="occurred_on", help="optional fuel stop date in YYYY-MM-DD form")
    add_fuel_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_fuel_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_stop_parser = subparsers.add_parser("add-stop", help="capture a memorable stop in binder-friendly form")
    add_stop_parser.add_argument("trip_slug", help="trip workspace slug")
    add_stop_parser.add_argument("name", help="stop name")
    add_stop_parser.add_argument("location", help="stop location")
    add_stop_parser.add_argument("notes", help="stop notes")
    add_stop_parser.add_argument("--date", dest="occurred_on", help="optional stop date in YYYY-MM-DD form")
    add_stop_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_stop_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_campground_parser = subparsers.add_parser("add-campground-review", help="capture a campground review in binder-friendly form")
    add_campground_parser.add_argument("trip_slug", help="trip workspace slug")
    add_campground_parser.add_argument("campground_name", help="campground name")
    add_campground_parser.add_argument("site", help="site identifier or description")
    add_campground_parser.add_argument("rating", help="rating out of 5")
    add_campground_parser.add_argument("would_return", help="yes/no or short return judgment")
    add_campground_parser.add_argument("notes", help="campground review notes")
    add_campground_parser.add_argument("--date", dest="occurred_on", help="optional review date in YYYY-MM-DD form")
    add_campground_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_campground_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_travel_parser = subparsers.add_parser("add-travel-day-note", help="capture a travel-day note in binder-friendly form")
    add_travel_parser.add_argument("trip_slug", help="trip workspace slug")
    add_travel_parser.add_argument("title", help="travel note title")
    add_travel_parser.add_argument("notes", help="travel note details")
    add_travel_parser.add_argument("--date", dest="occurred_on", help="optional travel-day date in YYYY-MM-DD form")
    add_travel_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_travel_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_mileage_parser = subparsers.add_parser("add-mileage-note", help="capture a mileage note in binder-friendly form")
    add_mileage_parser.add_argument("trip_slug", help="trip workspace slug")
    add_mileage_parser.add_argument("title", help="mileage note title")
    add_mileage_parser.add_argument("miles", help="miles for this note")
    add_mileage_parser.add_argument("notes", help="mileage note details")
    add_mileage_parser.add_argument("--date", dest="occurred_on", help="optional mileage date in YYYY-MM-DD form")
    add_mileage_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_mileage_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    add_daily_parser = subparsers.add_parser("add-daily-review", help="capture an end-of-day review in binder-friendly form")
    add_daily_parser.add_argument("trip_slug", help="trip workspace slug")
    add_daily_parser.add_argument("title", help="daily review title")
    add_daily_parser.add_argument("notes", help="daily review notes")
    add_daily_parser.add_argument("--date", dest="occurred_on", help="optional review date in YYYY-MM-DD form")
    add_daily_parser.add_argument("--travel-day-id", help="optional related travel day id")
    add_daily_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    checklist_parser = subparsers.add_parser("trip-checklist", help="show what is still missing for the current trip binder")
    checklist_parser.add_argument("trip_slug", help="trip workspace slug")
    checklist_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    daily_summary_parser = subparsers.add_parser("trip-daily-summary", help="summarize the captured binder items for a specific day")
    daily_summary_parser.add_argument("trip_slug", help="trip workspace slug")
    daily_summary_parser.add_argument("date", help="date to summarize in YYYY-MM-DD form")
    daily_summary_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    capture_prompts_parser = subparsers.add_parser("trip-capture-prompts", help="print grouped conversational prompts for missing binder areas")
    capture_prompts_parser.add_argument("trip_slug", help="trip workspace slug")
    capture_prompts_parser.add_argument("--date", dest="occurred_on", help="optional date to focus prompts on one trip day")
    capture_prompts_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    questions_parser = subparsers.add_parser("trip-questions", help="list follow-up questions for a live trip workspace")
    questions_parser.add_argument("trip_slug", help="trip workspace slug")
    questions_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    reflection_parser = subparsers.add_parser("add-final-reflection", help="store a final reflection for a completed trip binder")
    reflection_parser.add_argument("trip_slug", help="trip workspace slug")
    reflection_parser.add_argument("content", help="final reflection text")
    reflection_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    finalize_parser = subparsers.add_parser("finalize-trip", help="mark a trip complete and generate the final binder")
    finalize_parser.add_argument("trip_slug", help="trip workspace slug")
    finalize_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    render_current_parser = subparsers.add_parser("render-current-binder", help="render the current binder snapshot for a live trip workspace")
    render_current_parser.add_argument("trip_slug", help="trip workspace slug")
    render_current_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    render_current_html_parser = subparsers.add_parser("render-current-binder-html", help="render the current binder snapshot as HTML for a live trip workspace")
    render_current_html_parser.add_argument("trip_slug", help="trip workspace slug")
    render_current_html_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    render_final_html_parser = subparsers.add_parser("render-final-binder-html", help="render the final binder as HTML for a live trip workspace")
    render_final_html_parser.add_argument("trip_slug", help="trip workspace slug")
    render_final_html_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

    export_bundle_parser = subparsers.add_parser("trip-export-bundle", help="package trip binder outputs and notes into a zip bundle")
    export_bundle_parser.add_argument("trip_slug", help="trip workspace slug")
    export_bundle_parser.add_argument("--base-dir", default="data", help="base data directory that contains the trips/ folder")

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

    ingest_parser = subparsers.add_parser("ingest-csv", help="import a CSV, merge it into a trip, and validate the result")
    ingest_parser.add_argument("csv_type", choices=["fuel-stop", "expense"], help="CSV import type")
    ingest_parser.add_argument("trip", help="trip JSON file")
    ingest_parser.add_argument("input", help="input CSV file")
    ingest_parser.add_argument("output", help="output merged trip JSON file")
    ingest_parser.add_argument("--merge-mode", choices=["append", "replace"], default="append", help="merge mode to use when applying imported records")

    import_rtw_parser = subparsers.add_parser("import-rtw", help="import an RV Trip Wizard JSON export into trip JSON")
    import_rtw_parser.add_argument("input", help="input RV Trip Wizard export JSON file")
    import_rtw_parser.add_argument("output", help="output normalized trip JSON file")

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


def create_live_trip_command(trip_slug: str, rtw_input: str, base_dir: str = "data") -> int:
    try:
        root = create_live_trip(Path(base_dir), trip_slug, Path(rtw_input))
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created live trip workspace: {root}")
    return 0


def add_trip_note_command(trip_slug: str, note_type: str, content: str, base_dir: str = "data") -> int:
    try:
        note_path = add_trip_note(Path(base_dir), trip_slug, note_type, content)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added {note_type} note to {note_path}")
    return 0


def add_trip_entry_command(
    trip_slug: str,
    entry_type: str,
    title: str,
    content: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_trip_entry(
            Path(base_dir),
            trip_slug,
            entry_type,
            title,
            content,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added {entry_type} entry: {title}")
    return 0


def add_meal_command(
    trip_slug: str,
    restaurant: str,
    location: str,
    notes: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_meal(
            Path(base_dir),
            trip_slug,
            restaurant,
            location,
            notes,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added meal: {restaurant}")
    return 0


def add_fuel_stop_command(
    trip_slug: str,
    vendor: str,
    location: str,
    gallons: str,
    total_cost: str,
    odometer: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_fuel_stop(
            Path(base_dir),
            trip_slug,
            vendor,
            location,
            gallons,
            total_cost,
            odometer,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added fuel stop: {vendor}")
    return 0


def add_stop_command(
    trip_slug: str,
    name: str,
    location: str,
    notes: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_stop(
            Path(base_dir),
            trip_slug,
            name,
            location,
            notes,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added stop: {name}")
    return 0


def add_campground_review_command(
    trip_slug: str,
    campground_name: str,
    site: str,
    rating: str,
    would_return: str,
    notes: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_campground_review(
            Path(base_dir),
            trip_slug,
            campground_name,
            site,
            rating,
            would_return,
            notes,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added campground review: {campground_name}")
    return 0


def add_travel_day_note_command(
    trip_slug: str,
    title: str,
    notes: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_travel_day_note(
            Path(base_dir),
            trip_slug,
            title,
            notes,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added travel-day note: {title}")
    return 0


def add_mileage_note_command(
    trip_slug: str,
    title: str,
    miles: str,
    notes: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_mileage_note(
            Path(base_dir),
            trip_slug,
            title,
            miles,
            notes,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added mileage note: {title}")
    return 0


def add_daily_review_command(
    trip_slug: str,
    title: str,
    notes: str,
    base_dir: str = "data",
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> int:
    try:
        add_daily_review(
            Path(base_dir),
            trip_slug,
            title,
            notes,
            occurred_on=occurred_on,
            travel_day_id=travel_day_id,
        )
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added daily review: {title}")
    return 0


def trip_checklist_command(trip_slug: str, base_dir: str = "data") -> int:
    try:
        items = trip_checklist(Path(base_dir), trip_slug)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if not items:
        print("Trip binder checklist is clear.")
        return 0
    for item in items:
        print(item)
    return 0


def trip_daily_summary_command(trip_slug: str, date: str, base_dir: str = "data") -> int:
    try:
        summary = trip_daily_summary(Path(base_dir), trip_slug, date)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(summary, end="")
    return 0


def trip_capture_prompts_command(trip_slug: str, base_dir: str = "data", occurred_on: str | None = None) -> int:
    try:
        prompts = trip_capture_prompts(Path(base_dir), trip_slug, occurred_on)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(prompts, end="")
    return 0


def trip_questions_command(trip_slug: str, base_dir: str = "data") -> int:
    try:
        questions = follow_up_questions(Path(base_dir), trip_slug)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if not questions:
        print("No follow-up questions right now.")
        return 0
    for question in questions:
        print(question)
    return 0


def add_final_reflection_command(trip_slug: str, content: str, base_dir: str = "data") -> int:
    try:
        add_final_reflection(Path(base_dir), trip_slug, content)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Added final reflection for {trip_slug}")
    return 0


def finalize_trip_command(trip_slug: str, base_dir: str = "data") -> int:
    try:
        output_path = finalize_trip(Path(base_dir), trip_slug)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Finalized trip binder: {output_path}")
    return 0


def render_current_binder_command(trip_slug: str, base_dir: str = "data") -> int:
    try:
        output_path = render_current_binder(Path(base_dir), trip_slug)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Rendered current binder: {output_path}")
    return 0


def render_current_binder_html_command(trip_slug: str, base_dir: str = "data") -> int:
    try:
        output_path = render_current_binder_html(Path(base_dir), trip_slug)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Rendered current HTML binder: {output_path}")
    return 0


def render_final_binder_html_command(trip_slug: str, base_dir: str = "data") -> int:
    try:
        output_path = render_final_binder_html(Path(base_dir), trip_slug)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Rendered final HTML binder: {output_path}")
    return 0


def trip_export_bundle_command(trip_slug: str, base_dir: str = "data") -> int:
    try:
        output_path = export_trip_bundle(Path(base_dir), trip_slug)
    except LiveTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Exported trip bundle: {output_path}")
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


def ingest_csv_command(csv_type: str, trip_path: str, input_path: str, output_path: str, merge_mode: str = "append") -> int:
    try:
        merged = ingest_csv_to_trip(csv_type, Path(trip_path), Path(input_path), Path(output_path), merge_mode=merge_mode)
    except WorkflowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    travel_days = len(merged.get("travel_days", [])) if isinstance(merged, dict) else 0
    print(f"Ingested {csv_type} CSV into {output_path} with {travel_days} travel day(s) using {merge_mode} mode")
    return 0


def import_rtw_command(input_path: str, output_path: str) -> int:
    try:
        trip = import_rtw_file(Path(input_path), Path(output_path))
    except RvTripWizardImportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Imported RV Trip Wizard trip '{trip['name']}' to {output_path}")
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
    if args.command == "create-live-trip":
        return create_live_trip_command(args.trip_slug, args.rtw_input, args.base_dir)
    if args.command == "add-trip-note":
        return add_trip_note_command(args.trip_slug, args.note_type, args.content, args.base_dir)
    if args.command == "add-trip-entry":
        return add_trip_entry_command(
            args.trip_slug,
            args.entry_type,
            args.title,
            args.content,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "add-meal":
        return add_meal_command(
            args.trip_slug,
            args.restaurant,
            args.location,
            args.notes,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "add-fuel-stop":
        return add_fuel_stop_command(
            args.trip_slug,
            args.vendor,
            args.location,
            args.gallons,
            args.total_cost,
            args.odometer,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "add-stop":
        return add_stop_command(
            args.trip_slug,
            args.name,
            args.location,
            args.notes,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "add-campground-review":
        return add_campground_review_command(
            args.trip_slug,
            args.campground_name,
            args.site,
            args.rating,
            args.would_return,
            args.notes,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "add-travel-day-note":
        return add_travel_day_note_command(
            args.trip_slug,
            args.title,
            args.notes,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "add-mileage-note":
        return add_mileage_note_command(
            args.trip_slug,
            args.title,
            args.miles,
            args.notes,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "add-daily-review":
        return add_daily_review_command(
            args.trip_slug,
            args.title,
            args.notes,
            args.base_dir,
            args.occurred_on,
            args.travel_day_id,
        )
    if args.command == "trip-checklist":
        return trip_checklist_command(args.trip_slug, args.base_dir)
    if args.command == "trip-daily-summary":
        return trip_daily_summary_command(args.trip_slug, args.date, args.base_dir)
    if args.command == "trip-capture-prompts":
        return trip_capture_prompts_command(args.trip_slug, args.base_dir, args.occurred_on)
    if args.command == "trip-questions":
        return trip_questions_command(args.trip_slug, args.base_dir)
    if args.command == "add-final-reflection":
        return add_final_reflection_command(args.trip_slug, args.content, args.base_dir)
    if args.command == "finalize-trip":
        return finalize_trip_command(args.trip_slug, args.base_dir)
    if args.command == "render-current-binder":
        return render_current_binder_command(args.trip_slug, args.base_dir)
    if args.command == "render-current-binder-html":
        return render_current_binder_html_command(args.trip_slug, args.base_dir)
    if args.command == "render-final-binder-html":
        return render_final_binder_html_command(args.trip_slug, args.base_dir)
    if args.command == "trip-export-bundle":
        return trip_export_bundle_command(args.trip_slug, args.base_dir)
    if args.command == "render-html":
        return render_html_command(args.input, args.output)
    if args.command == "validate":
        return validate_command(args.input, args.schema)
    if args.command == "import-csv":
        return import_csv_command(args.csv_type, args.input, args.output)
    if args.command == "ingest-csv":
        return ingest_csv_command(args.csv_type, args.trip, args.input, args.output, args.merge_mode)
    if args.command == "import-rtw":
        return import_rtw_command(args.input, args.output)
    if args.command == "merge-records":
        return merge_records_command(args.record_type, args.trip, args.records, args.output, args.mode)
    if args.command == "validate-repo":
        return validate_repo_command()
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
