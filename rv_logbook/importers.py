"""CSV import helpers for RV Expedition Logbook."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class CsvImportError(Exception):
    """Raised when CSV import cannot proceed."""


IMPORT_SPECS: dict[str, dict[str, Any]] = {
    "fuel-stop": {
        "required": [
            "id",
            "travel_day_id",
            "date",
            "vendor",
            "location",
            "odometer",
            "gallons",
            "total_cost",
            "price_per_gallon",
            "notes",
        ],
        "numeric": {"odometer", "gallons", "total_cost", "price_per_gallon"},
    },
    "expense": {
        "required": ["id", "travel_day_id", "date", "category", "amount", "vendor", "notes"],
        "numeric": {"amount"},
    },
}


def import_csv(csv_type: str, input_path: Path) -> list[dict[str, Any]]:
    if csv_type not in IMPORT_SPECS:
        valid = ", ".join(sorted(IMPORT_SPECS))
        raise CsvImportError(f"unknown csv import type '{csv_type}'. Valid types: {valid}")

    spec = IMPORT_SPECS[csv_type]
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [column for column in spec["required"] if column not in fieldnames]
        if missing:
            raise CsvImportError(f"missing required columns: {', '.join(missing)}")

        rows: list[dict[str, Any]] = []
        for row in reader:
            record: dict[str, Any] = {}
            for key in spec["required"]:
                value = row.get(key, "")
                if key in spec["numeric"]:
                    try:
                        numeric = float(value)
                    except ValueError as exc:
                        raise CsvImportError(f"invalid numeric value for {key}: {value}") from exc
                    record[key] = int(numeric) if numeric.is_integer() else numeric
                else:
                    record[key] = value
            rows.append(record)
        return rows


def write_json(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
