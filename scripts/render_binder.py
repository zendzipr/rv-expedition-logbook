#!/usr/bin/env python3
"""Render a Markdown RV expedition binder from a trip JSON file.

This intentionally uses only the Python standard library so the repository works
on a fresh machine without dependency installation.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "binder"
DEFAULT_SECTIONS = [
    "cover.md",
    "trip-summary.md",
    "travel-day-dashboard.md",
    "fuel-log.md",
    "expense-log.md",
    "maintenance-log.md",
    "captain-log.md",
]

PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z0-9_.]+)\s*}}")


class BinderRenderError(Exception):
    """Raised when binder input cannot be rendered."""


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"input file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        fail("trip input must be a JSON object")
    return data


def require_fields(obj: dict[str, Any], fields: list[str], label: str) -> None:
    for field in fields:
        if field not in obj or obj[field] in (None, ""):
            raise BinderRenderError(f"{label} missing required field: {field}")


def validate_trip(trip: dict[str, Any]) -> None:
    require_fields(trip, ["id", "name", "start_date"], "Trip")
    for index, travel_day in enumerate(trip.get("travel_days", []), start=1):
        if not isinstance(travel_day, dict):
            raise BinderRenderError(f"TravelDay #{index} must be an object")
        require_fields(travel_day, ["id", "trip_id", "date"], f"TravelDay #{index}")


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def markdown_value(value: Any, block: bool = False) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        if not value:
            return ""
        if block:
            return "\n".join(f"- {markdown_value(item)}" for item in value)
        return ", ".join(markdown_value(item) for item in value)
    if isinstance(value, dict):
        if not value:
            return ""
        return ", ".join(f"{key}: {markdown_value(val)}" for key, val in value.items())
    return str(value)


def lookup(context: dict[str, Any], dotted_path: str) -> Any:
    current: Any = context
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return ""
    return current


def render_template(template: str, context: dict[str, Any]) -> str:
    rendered_lines: list[str] = []
    for line in template.splitlines():
        stripped = line.strip()
        block_match = PLACEHOLDER_RE.fullmatch(stripped)
        if block_match:
            indent = line[: len(line) - len(line.lstrip())]
            value = markdown_value(lookup(context, block_match.group(1)), block=True)
            if value:
                rendered_lines.extend(indent + value_line for value_line in value.splitlines())
            else:
                rendered_lines.append("")
            continue

        def replace(match: re.Match[str]) -> str:
            return markdown_value(lookup(context, match.group(1)))

        rendered_lines.append(PLACEHOLDER_RE.sub(replace, line))

    return "\n".join(rendered_lines).strip() + "\n"


def money(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def number(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric.is_integer():
        return str(int(numeric))
    return f"{numeric:,.2f}"


def table_row(values: list[Any], money_columns: set[int] | None = None) -> str:
    money_columns = money_columns or set()
    cells = []
    for index, value in enumerate(values):
        cells.append(money(value) if index in money_columns else markdown_value(value).replace("\n", " "))
    return "| " + " | ".join(cells) + " |"


def collect_nested(trip: dict[str, Any], key: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for travel_day in trip.get("travel_days", []):
        if not isinstance(travel_day, dict):
            continue
        for record in as_list(travel_day.get(key)):
            if isinstance(record, dict):
                record.setdefault("travel_day_id", travel_day.get("id", ""))
                records.append(record)
    for record in as_list(trip.get(key)):
        if isinstance(record, dict):
            records.append(record)
    return records


def build_trip_context(trip: dict[str, Any]) -> dict[str, Any]:
    travel_days = [day for day in trip.get("travel_days", []) if isinstance(day, dict)]
    total_miles = sum(float(day.get("miles", 0) or 0) for day in travel_days)
    fuel_stops = collect_nested(trip, "fuel_stops")
    expenses = collect_nested(trip, "expenses")
    maintenance = collect_nested(trip, "maintenance_events")

    total_fuel_cost = sum(float(stop.get("total_cost", 0) or 0) for stop in fuel_stops)
    total_expense_cost = sum(float(expense.get("amount", 0) or 0) for expense in expenses)
    total_maintenance_cost = sum(float(event.get("cost", 0) or 0) for event in maintenance)

    enriched = dict(trip)
    enriched.setdefault("end_date", "")
    enriched["total_miles"] = number(total_miles)
    enriched["campground_count"] = len([day for day in travel_days if day.get("campground")])
    enriched["fuel_cost"] = money(total_fuel_cost)
    enriched["total_cost"] = money(total_fuel_cost + total_expense_cost + total_maintenance_cost)
    enriched["highlights"] = [item for day in travel_days for item in as_list(day.get("highlights"))]
    enriched["lessons_learned"] = [item for day in travel_days for item in as_list(day.get("lessons_learned"))]
    return enriched


def render_tables(trip: dict[str, Any]) -> dict[str, str]:
    fuel_rows = [
        table_row(
            [
                stop.get("date", ""),
                stop.get("vendor", ""),
                stop.get("location", ""),
                number(stop.get("odometer")),
                number(stop.get("gallons")),
                stop.get("total_cost", ""),
                money(stop.get("price_per_gallon")) if stop.get("price_per_gallon") not in (None, "") else "",
            ],
            money_columns={5},
        )
        for stop in collect_nested(trip, "fuel_stops")
    ]
    expense_rows = [
        table_row(
            [expense.get("date", ""), expense.get("category", ""), expense.get("vendor", ""), expense.get("amount", ""), expense.get("notes", "")],
            money_columns={3},
        )
        for expense in collect_nested(trip, "expenses")
    ]
    maintenance_rows = [
        table_row(
            [
                event.get("date", ""),
                event.get("system", ""),
                event.get("title", ""),
                event.get("status", ""),
                event.get("cost", ""),
                event.get("follow_up", ""),
            ],
            money_columns={4},
        )
        for event in collect_nested(trip, "maintenance_events")
    ]
    return {
        "fuel_rows": "\n".join(fuel_rows) if fuel_rows else "|  |  |  |  |  |  |  |",
        "expense_rows": "\n".join(expense_rows) if expense_rows else "|  |  |  |  |  |",
        "maintenance_rows": "\n".join(maintenance_rows) if maintenance_rows else "|  |  |  |  |  |  |",
    }


def render_binder(trip: dict[str, Any]) -> str:
    validate_trip(trip)
    trip_context = build_trip_context(trip)
    table_context = render_tables(trip)
    sections: list[str] = []

    # Trip-level pages.
    for template_name in ("cover.md", "trip-summary.md"):
        template = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        sections.append(render_template(template, {"trip": trip_context, **table_context}))

    # Per-travel-day pages.
    travel_template = (TEMPLATE_DIR / "travel-day-dashboard.md").read_text(encoding="utf-8")
    campground_template = (TEMPLATE_DIR / "campground-review.md").read_text(encoding="utf-8")
    captain_template = (TEMPLATE_DIR / "captain-log.md").read_text(encoding="utf-8")
    for travel_day in trip.get("travel_days", []):
        if not isinstance(travel_day, dict):
            continue
        day_context = dict(travel_day)
        day_context.setdefault("drive_time", minutes_to_duration(day_context.get("drive_time_minutes")))
        day_context.setdefault("arrival_notes", "")
        sections.append(render_template(travel_template, {"travel_day": day_context}))
        if isinstance(day_context.get("campground"), dict):
            sections.append(render_template(campground_template, {"campground": day_context["campground"]}))
        journal_entries = as_list(day_context.get("journal_entries"))
        for entry in journal_entries:
            if isinstance(entry, dict):
                sections.append(render_template(captain_template, {"entry": entry}))

    # Log pages.
    for template_name in ("fuel-log.md", "expense-log.md", "maintenance-log.md"):
        template = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        sections.append(render_template(template, table_context))

    return "\n---\n\n".join(sections).strip() + "\n"


def minutes_to_duration(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return str(value)
    hours, remainder = divmod(minutes, 60)
    if hours and remainder:
        return f"{hours}h {remainder}m"
    if hours:
        return f"{hours}h"
    return f"{remainder}m"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: render_binder.py <trip.json> <output.md>", file=sys.stderr)
        return 2

    input_path = Path(argv[1])
    output_path = Path(argv[2])
    trip = load_json(input_path)
    try:
        rendered = render_binder(trip)
    except BinderRenderError as exc:
        fail(str(exc))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Rendered binder: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
