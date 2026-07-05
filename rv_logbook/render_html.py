"""Render an HTML RV expedition report from trip JSON."""
from __future__ import annotations

from html import escape
from typing import Any

from .domain import Trip, as_list, money, number
from .render import BinderRenderError, validate_trip


def html_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    return escape(str(value))


def render_list(items: list[Any]) -> str:
    if not items:
        return "<p class=\"muted\">None recorded.</p>"
    rendered = "".join(f"<li>{html_value(item)}</li>" for item in items)
    return f"<ul>{rendered}</ul>"


def render_key_value_rows(items: list[tuple[str, Any]]) -> str:
    rows = "".join(
        f"<tr><th>{escape(label)}</th><td>{html_value(value)}</td></tr>" for label, value in items
    )
    return f"<table class=\"kv\">{rows}</table>"


def render_records_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "<p class=\"muted\">No records.</p>"
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html_value(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def render_html_report(trip_data: dict[str, Any]) -> str:
    validate_trip(trip_data)
    trip = Trip.from_dict(trip_data)
    trip_context = trip.to_template_context()

    travel_day_sections: list[str] = []
    for day in trip.travel_days:
        day_context = day.to_template_context()
        campground_html = ""
        campground = day_context.get("campground")
        if isinstance(campground, dict):
            campground_html = (
                "<section><h4>Campground</h4>"
                + render_key_value_rows(
                    [
                        ("Name", campground.get("name", "")),
                        ("Location", campground.get("location", "")),
                        ("Site", campground.get("site", "")),
                        ("Hookups", ", ".join(as_list(campground.get("hookups")))),
                        ("Connectivity", ", ".join(f"{k}: {v}" for k, v in campground.get("connectivity", {}).items())),
                        ("Rating", f"{campground.get('rating', '')}/5" if campground.get("rating") not in (None, "") else ""),
                        ("Would Return", "yes" if campground.get("would_return") else "no"),
                    ]
                )
                + f"<p>{html_value(campground.get('notes', ''))}</p></section>"
            )

        journal_html = ""
        journal_entries = [entry for entry in as_list(day_context.get("journal_entries")) if isinstance(entry, dict)]
        if journal_entries:
            journal_bits = []
            for entry in journal_entries:
                journal_bits.append(
                    f"<article class=\"journal-entry\"><h4>{html_value(entry.get('date', ''))}</h4>"
                    f"<p>{html_value(entry.get('body', ''))}</p>"
                    f"<h5>Lessons</h5>{render_list(as_list(entry.get('lessons')))}</article>"
                )
            journal_html = "<section><h4>Captain's Log</h4>" + "".join(journal_bits) + "</section>"

        travel_day_sections.append(
            "<section class=\"travel-day\">"
            f"<h3>Travel Day: {html_value(day.date)}</h3>"
            + render_key_value_rows(
                [
                    ("Origin", day_context.get("origin", "")),
                    ("Destination", day_context.get("destination", "")),
                    ("Miles", number(day_context.get("miles"))),
                    ("Drive Time", day_context.get("drive_time", "")),
                    ("Weather", day_context.get("weather", "")),
                ]
            )
            + f"<h4>Route Notes</h4><p>{html_value(day_context.get('route_notes', ''))}</p>"
            + f"<h4>Arrival / Setup Notes</h4><p>{html_value(day_context.get('arrival_notes', ''))}</p>"
            + f"<h4>Highlights</h4>{render_list(day.highlights)}"
            + f"<h4>Lessons Learned</h4>{render_list(day.lessons_learned)}"
            + campground_html
            + journal_html
            + "</section>"
        )

    fuel_rows = [
        [
            stop.get("date", ""),
            stop.get("vendor", ""),
            stop.get("location", ""),
            number(stop.get("odometer")),
            number(stop.get("gallons")),
            money(stop.get("total_cost")),
            money(stop.get("price_per_gallon")),
        ]
        for stop in trip.fuel_stops
    ]
    expense_rows = [
        [
            expense.get("date", ""),
            expense.get("category", ""),
            expense.get("vendor", ""),
            money(expense.get("amount")),
            expense.get("notes", ""),
        ]
        for expense in trip.expenses
    ]
    maintenance_rows = [
        [
            event.get("date", ""),
            event.get("system", ""),
            event.get("title", ""),
            event.get("status", ""),
            money(event.get("cost")),
            event.get("follow_up", ""),
        ]
        for event in trip.maintenance_events
    ]

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html_value(trip.name)} - RV Expedition Logbook</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem auto; max-width: 1100px; padding: 0 1rem; color: #1f2937; background: #f8fafc; }}
    h1, h2, h3, h4, h5 {{ color: #0f172a; }}
    .card, .travel-day {{ background: white; border: 1px solid #dbeafe; border-radius: 12px; padding: 1rem 1.25rem; margin: 1rem 0; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
    table {{ width: 100%; border-collapse: collapse; background: white; margin: 0.75rem 0 1.5rem; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 0.5rem 0.65rem; text-align: left; vertical-align: top; }}
    th {{ background: #e2e8f0; }}
    .kv th {{ width: 18rem; }}
    .muted {{ color: #64748b; }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; }}
    .stat {{ background: white; border: 1px solid #dbeafe; border-radius: 10px; padding: 0.75rem; }}
    code {{ background: #e2e8f0; padding: 0.1rem 0.3rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <header class=\"card\">
    <h1>{html_value(trip.name)}</h1>
    <p><strong>Dates:</strong> {html_value(trip.start_date)} – {html_value(trip_context.get('end_date', ''))}</p>
    <p><strong>Travelers:</strong> {html_value(', '.join(as_list(trip_context.get('travelers'))))}</p>
    <p>{html_value(trip_context.get('summary', ''))}</p>
  </header>

  <section class=\"card\">
    <h2>Trip Summary</h2>
    <div class=\"stats\">
      <div class=\"stat\"><strong>Total Miles</strong><br>{html_value(trip_context.get('total_miles', ''))}</div>
      <div class=\"stat\"><strong>Campgrounds</strong><br>{html_value(trip_context.get('campground_count', ''))}</div>
      <div class=\"stat\"><strong>Fuel Cost</strong><br>{html_value(trip_context.get('fuel_cost', ''))}</div>
      <div class=\"stat\"><strong>Total Cost</strong><br>{html_value(trip_context.get('total_cost', ''))}</div>
    </div>
    <h3>Highlights</h3>
    {render_list(trip.highlights)}
    <h3>Lessons Learned</h3>
    {render_list(trip.lessons_learned)}
  </section>

  <section>
    <h2>Travel Day Details</h2>
    {''.join(travel_day_sections)}
  </section>

  <section class=\"card\">
    <h2>Fuel Stops</h2>
    {render_records_table(['Date', 'Vendor', 'Location', 'Odometer', 'Gallons', 'Total', 'Price/Gal'], fuel_rows)}
  </section>

  <section class=\"card\">
    <h2>Expenses</h2>
    {render_records_table(['Date', 'Category', 'Vendor', 'Amount', 'Notes'], expense_rows)}
  </section>

  <section class=\"card\">
    <h2>Maintenance</h2>
    {render_records_table(['Date', 'System', 'Title', 'Status', 'Cost', 'Follow-up'], maintenance_rows)}
  </section>
</body>
</html>
"""


def render_html(trip_data: dict[str, Any]) -> str:
    try:
        return render_html_report(trip_data)
    except BinderRenderError:
        raise
