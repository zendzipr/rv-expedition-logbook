"""Higher-level workflow commands built from import, merge, and validation steps."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .importers import CsvImportError, import_csv
from .merge import MergeError, merge_records
from .schema import SchemaValidationError, validate_data


class WorkflowError(Exception):
    """Raised when a composed workflow command fails."""


def ingest_csv_to_trip(csv_type: str, trip_path: Path, csv_path: Path, output_path: Path, merge_mode: str = "append") -> dict[str, Any]:
    try:
        trip = json.loads(trip_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"invalid JSON in trip file: {trip_path}") from exc

    if not isinstance(trip, dict):
        raise WorkflowError("trip input must be a JSON object")

    try:
        imported_records = import_csv(csv_type, csv_path)
        merged = merge_records(csv_type, trip, imported_records, mode=merge_mode)
        validate_data(merged, "trip")
    except (CsvImportError, MergeError, SchemaValidationError) as exc:
        raise WorkflowError(str(exc)) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return merged
