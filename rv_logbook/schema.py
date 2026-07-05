"""JSON Schema validation for RV Expedition Logbook data."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, RefResolver
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"

SCHEMA_NAMES = {
    "trip": "trip.schema.json",
    "travel-day": "travel-day.schema.json",
    "campground": "campground.schema.json",
    "fuel-stop": "fuel-stop.schema.json",
    "expense": "expense.schema.json",
    "maintenance-event": "maintenance-event.schema.json",
    "provenance": "provenance.schema.json",
}


class SchemaValidationError(Exception):
    """Raised when data does not match a project JSON Schema."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(schema_name: str) -> dict[str, Any]:
    if schema_name not in SCHEMA_NAMES:
        valid = ", ".join(sorted(SCHEMA_NAMES))
        raise SchemaValidationError(f"unknown schema '{schema_name}'. Valid schemas: {valid}")
    return load_json(SCHEMA_DIR / SCHEMA_NAMES[schema_name])


def schema_store() -> dict[str, dict[str, Any]]:
    store: dict[str, dict[str, Any]] = {}
    for path in SCHEMA_DIR.glob("*.schema.json"):
        schema = load_json(path)
        store[path.name] = schema
        if "$id" in schema:
            store[schema["$id"]] = schema
    return store


def validate_data(data: Any, schema_name: str) -> None:
    schema = load_schema(schema_name)
    resolver = RefResolver.from_schema(schema, store=schema_store())
    validator = Draft202012Validator(schema, resolver=resolver)
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        raise SchemaValidationError(format_error(errors[0]))


def validate_file(path: Path, schema_name: str) -> None:
    validate_data(load_json(path), schema_name)


def validate_repository() -> list[str]:
    checked: list[str] = []
    for schema_path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        checked.append(str(schema_path.relative_to(ROOT)))

    validate_file(ROOT / "examples" / "sample-trip.json", "trip")
    checked.append("examples/sample-trip.json")
    return checked


def format_error(error: JsonSchemaValidationError) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message
