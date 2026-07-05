"""RV Trip Wizard connector scaffold."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class RvTripWizardImportError(Exception):
    """Raised when an RV Trip Wizard export cannot be normalized."""


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "trip"


def load_rtw_export(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RvTripWizardImportError("RV Trip Wizard export must be a JSON object")
    return data


def import_rtw_export(data: dict[str, Any]) -> dict[str, Any]:
    trip_name = data.get("trip_name")
    start_date = data.get("start_date")
    stops = data.get("stops")

    if not trip_name:
        raise RvTripWizardImportError("RV Trip Wizard export missing trip_name")
    if not start_date:
        raise RvTripWizardImportError("RV Trip Wizard export missing start_date")
    if not isinstance(stops, list) or not stops:
        raise RvTripWizardImportError("RV Trip Wizard export missing stops list")

    trip_id = _slugify(str(trip_name))
    travel_days: list[dict[str, Any]] = []
    for index, stop in enumerate(stops, start=1):
        if not isinstance(stop, dict):
            raise RvTripWizardImportError(f"stop #{index} must be an object")
        stop_date = stop.get("date")
        stop_name = stop.get("name")
        if not stop_date:
            raise RvTripWizardImportError(f"stop #{index} missing date")
        if not stop_name:
            raise RvTripWizardImportError(f"stop #{index} missing name")

        day_id = str(stop.get("travel_day_id") or stop.get("stop_id") or f"{trip_id}-day-{index:03d}")
        campground = {
            "id": str(stop.get("campground_id") or stop.get("stop_id") or f"{trip_id}-campground-{index:03d}"),
            "name": str(stop_name),
            "location": stop.get("location", ""),
            "site": stop.get("site", ""),
            "notes": stop.get("reservation_notes", ""),
            "provenance": {
                "source": "rv-trip-wizard",
                "source_ref": str(stop.get("stop_id", "")),
            },
        }
        expenses: list[dict[str, Any]] = []
        nightly_cost = stop.get("nightly_cost")
        if nightly_cost not in (None, ""):
            expenses.append(
                {
                    "id": f"{day_id}-campground-expense",
                    "travel_day_id": day_id,
                    "date": stop_date,
                    "category": "campground",
                    "amount": float(nightly_cost),
                    "vendor": str(stop_name),
                    "notes": "Imported from RV Trip Wizard nightly cost.",
                    "provenance": {
                        "source": "rv-trip-wizard",
                        "source_ref": str(stop.get("stop_id", "")),
                    },
                }
            )

        travel_days.append(
            {
                "id": day_id,
                "trip_id": trip_id,
                "date": stop_date,
                "destination": str(stop_name),
                "miles": stop.get("distance_miles", 0),
                "route_notes": stop.get("route_notes", ""),
                "campground": campground,
                "expenses": expenses,
                "provenance": {
                    "source": "rv-trip-wizard",
                    "source_ref": str(stop.get("stop_id", "")),
                },
            }
        )

    return {
        "id": trip_id,
        "name": str(trip_name),
        "start_date": str(start_date),
        "end_date": str(data.get("end_date", "")) if data.get("end_date") not in (None, "") else None,
        "summary": "Imported from RV Trip Wizard export.",
        "travel_days": travel_days,
        "provenance": {
            "source": "rv-trip-wizard",
            "source_ref": Path(str(data.get("source_file", "rv-trip-wizard-export"))).name,
        },
    }


def import_rtw_file(input_path: Path, output_path: Path) -> dict[str, Any]:
    trip = import_rtw_export(load_rtw_export(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(trip, indent=2) + "\n", encoding="utf-8")
    return trip
