"""Merge imported record arrays into a trip JSON document."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MergeError(Exception):
    """Raised when imported records cannot be merged into a trip."""


MERGE_TARGETS = {
    "fuel-stop": "fuel_stops",
    "expense": "expenses",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_records(record_type: str, trip: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    if record_type not in MERGE_TARGETS:
        valid = ", ".join(sorted(MERGE_TARGETS))
        raise MergeError(f"unknown merge record type '{record_type}'. Valid types: {valid}")

    target_key = MERGE_TARGETS[record_type]
    merged = dict(trip)
    merged_days = []
    travel_days = merged.get("travel_days", [])
    travel_day_ids = {day.get("id") for day in travel_days if isinstance(day, dict)}

    for record in records:
        travel_day_id = record.get("travel_day_id")
        if travel_day_id not in travel_day_ids:
            raise MergeError(f"unknown travel_day_id: {travel_day_id}")

    by_day: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_day.setdefault(str(record.get("travel_day_id")), []).append(dict(record))

    for day in travel_days:
        if not isinstance(day, dict):
            merged_days.append(day)
            continue
        updated_day = dict(day)
        existing = updated_day.get(target_key)
        if existing is None:
            existing_records: list[Any] = []
        elif isinstance(existing, list):
            existing_records = list(existing)
        else:
            existing_records = [existing]
        additions = by_day.get(str(day.get("id")), [])
        updated_day[target_key] = existing_records + additions
        merged_days.append(updated_day)

    merged["travel_days"] = merged_days
    return merged


def merge_record_files(record_type: str, trip_path: Path, records_path: Path, output_path: Path) -> dict[str, Any]:
    trip = load_json(trip_path)
    records = load_json(records_path)
    if not isinstance(trip, dict):
        raise MergeError("trip input must be a JSON object")
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        raise MergeError("records input must be a JSON array of objects")
    merged = merge_records(record_type, trip, records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return merged
