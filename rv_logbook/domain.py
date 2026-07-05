"""Typed domain objects for RV Expedition Logbook data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


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


def numeric(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


@dataclass(slots=True)
class TravelDay:
    id: str
    trip_id: str
    date: str
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TravelDay":
        return cls(
            id=str(data.get("id", "")),
            trip_id=str(data.get("trip_id", "")),
            date=str(data.get("date", "")),
            data=dict(data),
        )

    @property
    def miles(self) -> float:
        return numeric(self.data.get("miles"))

    @property
    def campground(self) -> dict[str, Any] | None:
        campground = self.data.get("campground")
        return campground if isinstance(campground, dict) else None

    @property
    def highlights(self) -> list[Any]:
        return as_list(self.data.get("highlights"))

    @property
    def lessons_learned(self) -> list[Any]:
        return as_list(self.data.get("lessons_learned"))

    @property
    def fuel_stops(self) -> list[dict[str, Any]]:
        return self._nested_records("fuel_stops")

    @property
    def expenses(self) -> list[dict[str, Any]]:
        return self._nested_records("expenses")

    @property
    def maintenance_events(self) -> list[dict[str, Any]]:
        return self._nested_records("maintenance_events")

    @property
    def drive_time(self) -> str:
        return minutes_to_duration(self.data.get("drive_time_minutes"))

    def _nested_records(self, key: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for record in as_list(self.data.get(key)):
            if isinstance(record, dict):
                enriched = dict(record)
                enriched.setdefault("travel_day_id", self.id)
                records.append(enriched)
        return records

    def to_template_context(self) -> dict[str, Any]:
        context = dict(self.data)
        context.setdefault("drive_time", self.drive_time)
        context.setdefault("arrival_notes", "")
        return context


@dataclass(slots=True)
class Trip:
    id: str
    name: str
    start_date: str
    data: dict[str, Any] = field(default_factory=dict)
    travel_days: list[TravelDay] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Trip":
        travel_days = [TravelDay.from_dict(day) for day in data.get("travel_days", []) if isinstance(day, dict)]
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            start_date=str(data.get("start_date", "")),
            data=dict(data),
            travel_days=travel_days,
        )

    @property
    def total_miles(self) -> float:
        return sum(day.miles for day in self.travel_days)

    @property
    def campground_count(self) -> int:
        return len([day for day in self.travel_days if day.campground])

    @property
    def fuel_stops(self) -> list[dict[str, Any]]:
        return [record for day in self.travel_days for record in day.fuel_stops] + self._top_level_records("fuel_stops")

    @property
    def expenses(self) -> list[dict[str, Any]]:
        return [record for day in self.travel_days for record in day.expenses] + self._top_level_records("expenses")

    @property
    def maintenance_events(self) -> list[dict[str, Any]]:
        return [record for day in self.travel_days for record in day.maintenance_events] + self._top_level_records("maintenance_events")

    @property
    def total_fuel_cost(self) -> float:
        return sum(numeric(stop.get("total_cost")) for stop in self.fuel_stops)

    @property
    def total_expense_cost(self) -> float:
        return sum(numeric(expense.get("amount")) for expense in self.expenses)

    @property
    def total_maintenance_cost(self) -> float:
        return sum(numeric(event.get("cost")) for event in self.maintenance_events)

    @property
    def total_cost(self) -> float:
        return self.total_fuel_cost + self.total_expense_cost + self.total_maintenance_cost

    @property
    def highlights(self) -> list[Any]:
        return [item for day in self.travel_days for item in day.highlights]

    @property
    def lessons_learned(self) -> list[Any]:
        return [item for day in self.travel_days for item in day.lessons_learned]

    def _top_level_records(self, key: str) -> list[dict[str, Any]]:
        return [record for record in as_list(self.data.get(key)) if isinstance(record, dict)]

    def to_template_context(self) -> dict[str, Any]:
        context = dict(self.data)
        context.setdefault("end_date", "")
        context["total_miles"] = number(self.total_miles)
        context["campground_count"] = self.campground_count
        context["fuel_cost"] = money(self.total_fuel_cost)
        context["total_cost"] = money(self.total_cost)
        context["highlights"] = self.highlights
        context["lessons_learned"] = self.lessons_learned
        return context
