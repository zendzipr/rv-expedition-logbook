"""Live trip workspace helpers for binder-first trip management."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from .render import load_json, render_binder
from .render_html import render_html
from .rv_trip_wizard import RvTripWizardImportError, import_rtw_file


class LiveTripError(Exception):
    """Raised when live trip workspace operations fail."""


NOTE_FILES = {
    "daily": "daily-notes.md",
    "campground": "campground-notes.md",
    "meal": "meal-notes.md",
    "travel": "travel-notes.md",
    "stop": "stop-notes.md",
    "general": "general-notes.md",
}

ENTRY_TYPES = {"meal", "stop", "campground", "travel", "fuel", "mileage", "general"}
SECTION_TITLES = {
    "meal": "Meals",
    "stop": "Stops",
    "campground": "Campgrounds",
    "travel": "Travel Notes",
    "fuel": "Fuel & Mileage",
    "mileage": "Fuel & Mileage",
    "general": "General Notes",
}

QUESTION_RULES = [
    ("meal", "What meals were memorable on this part of the trip?"),
    ("stop", "Any memorable stops, attractions, or quick detours worth preserving in the binder?"),
    ("campground", "How was the campground in practice — site quality, hookups, noise, and whether you would stay again?"),
    ("travel", "What travel-day notes should be captured — weather, road conditions, or route lessons learned?"),
]


def trips_root(base_dir: Path) -> Path:
    return base_dir / "trips"


def trip_dir(base_dir: Path, trip_slug: str) -> Path:
    return trips_root(base_dir) / trip_slug


def trip_paths(base_dir: Path, trip_slug: str) -> dict[str, Path]:
    root = trip_dir(base_dir, trip_slug)
    return {
        "root": root,
        "trip_json": root / "trip.json",
        "db": root / "trip.db",
        "notes": root / "notes",
        "imports": root / "imports",
        "output": root / "output",
    }


def ensure_workspace_dirs(base_dir: Path, trip_slug: str) -> dict[str, Path]:
    paths = trip_paths(base_dir, trip_slug)
    for key in ("root", "notes", "imports", "output"):
        paths[key].mkdir(parents=True, exist_ok=True)
    for note_file in NOTE_FILES.values():
        note_path = paths["notes"] / note_file
        note_path.touch(exist_ok=True)
    return paths


def init_trip_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            create table if not exists trip_notes (
              id integer primary key autoincrement,
              note_type text not null,
              content text not null,
              created_at text not null
            )
            """
        )
        conn.execute(
            """
            create table if not exists trip_entries (
              id integer primary key autoincrement,
              entry_type text not null,
              title text not null,
              content text not null,
              occurred_on text,
              travel_day_id text,
              created_at text not null
            )
            """
        )
        columns = {row[1] for row in conn.execute("pragma table_info(trip_entries)").fetchall()}
        if "occurred_on" not in columns:
            conn.execute("alter table trip_entries add column occurred_on text")
        if "travel_day_id" not in columns:
            conn.execute("alter table trip_entries add column travel_day_id text")
        conn.execute(
            """
            create table if not exists final_reflections (
              id integer primary key autoincrement,
              content text not null,
              created_at text not null
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_live_trip(base_dir: Path, trip_slug: str, rtw_input: Path) -> Path:
    paths = ensure_workspace_dirs(base_dir, trip_slug)
    try:
        import_rtw_file(rtw_input, paths["trip_json"])
    except RvTripWizardImportError as exc:
        raise LiveTripError(str(exc)) from exc
    init_trip_db(paths["db"])
    return paths["root"]


def require_workspace(base_dir: Path, trip_slug: str) -> dict[str, Path]:
    paths = trip_paths(base_dir, trip_slug)
    if not paths["trip_json"].exists():
        raise LiveTripError(f"trip workspace not found: {trip_slug}")
    init_trip_db(paths["db"])
    return paths


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_trip_note(base_dir: Path, trip_slug: str, note_type: str, content: str) -> Path:
    if note_type not in NOTE_FILES:
        valid = ", ".join(sorted(NOTE_FILES))
        raise LiveTripError(f"unknown note type '{note_type}'. Valid types: {valid}")
    paths = require_workspace(base_dir, trip_slug)

    timestamp = utc_now()
    note_path = paths["notes"] / NOTE_FILES[note_type]
    with note_path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {timestamp}\n\n{content}\n")

    conn = sqlite3.connect(paths["db"])
    try:
        conn.execute(
            "insert into trip_notes(note_type, content, created_at) values (?, ?, ?)",
            (note_type, content, timestamp),
        )
        conn.commit()
    finally:
        conn.close()
    return note_path


def add_trip_entry(
    base_dir: Path,
    trip_slug: str,
    entry_type: str,
    title: str,
    content: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    if entry_type not in ENTRY_TYPES:
        valid = ", ".join(sorted(ENTRY_TYPES))
        raise LiveTripError(f"unknown entry type '{entry_type}'. Valid types: {valid}")
    paths = require_workspace(base_dir, trip_slug)
    conn = sqlite3.connect(paths["db"])
    try:
        conn.execute(
            "insert into trip_entries(entry_type, title, content, occurred_on, travel_day_id, created_at) values (?, ?, ?, ?, ?, ?)",
            (entry_type, title, content, occurred_on, travel_day_id, utc_now()),
        )
        conn.commit()
    finally:
        conn.close()


def add_meal(
    base_dir: Path,
    trip_slug: str,
    restaurant: str,
    location: str,
    notes: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    content = f"Location: {location}\n\n{notes}"
    add_trip_entry(
        base_dir,
        trip_slug,
        "meal",
        restaurant,
        content,
        occurred_on=occurred_on,
        travel_day_id=travel_day_id,
    )


def add_fuel_stop(
    base_dir: Path,
    trip_slug: str,
    vendor: str,
    location: str,
    gallons: str,
    total_cost: str,
    odometer: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    content = (
        f"Location: {location}\n\n"
        f"{gallons} gallons\n"
        f"Total: ${total_cost}\n"
        f"Odometer: {odometer}"
    )
    add_trip_entry(
        base_dir,
        trip_slug,
        "fuel",
        vendor,
        content,
        occurred_on=occurred_on,
        travel_day_id=travel_day_id,
    )


def add_stop(
    base_dir: Path,
    trip_slug: str,
    name: str,
    location: str,
    notes: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    content = f"Location: {location}\n\n{notes}"
    add_trip_entry(
        base_dir,
        trip_slug,
        "stop",
        name,
        content,
        occurred_on=occurred_on,
        travel_day_id=travel_day_id,
    )


def add_campground_review(
    base_dir: Path,
    trip_slug: str,
    campground_name: str,
    site: str,
    rating: str,
    would_return: str,
    notes: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    content = (
        f"Site: {site}\n"
        f"Rating: {rating}/5\n"
        f"Would return: {would_return}\n\n"
        f"{notes}"
    )
    add_trip_entry(
        base_dir,
        trip_slug,
        "campground",
        campground_name,
        content,
        occurred_on=occurred_on,
        travel_day_id=travel_day_id,
    )


def add_travel_day_note(
    base_dir: Path,
    trip_slug: str,
    title: str,
    notes: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    add_trip_entry(
        base_dir,
        trip_slug,
        "travel",
        title,
        notes,
        occurred_on=occurred_on,
        travel_day_id=travel_day_id,
    )


def add_mileage_note(
    base_dir: Path,
    trip_slug: str,
    title: str,
    miles: str,
    notes: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    content = f"Miles: {miles}\n\n{notes}"
    add_trip_entry(
        base_dir,
        trip_slug,
        "mileage",
        title,
        content,
        occurred_on=occurred_on,
        travel_day_id=travel_day_id,
    )


def add_daily_review(
    base_dir: Path,
    trip_slug: str,
    title: str,
    notes: str,
    occurred_on: str | None = None,
    travel_day_id: str | None = None,
) -> None:
    add_trip_note(base_dir, trip_slug, "daily", notes)
    add_travel_day_note(
        base_dir,
        trip_slug,
        title,
        notes,
        occurred_on=occurred_on,
        travel_day_id=travel_day_id,
    )


def add_final_reflection(base_dir: Path, trip_slug: str, content: str) -> None:
    paths = require_workspace(base_dir, trip_slug)
    conn = sqlite3.connect(paths["db"])
    try:
        conn.execute(
            "insert into final_reflections(content, created_at) values (?, ?)",
            (content, utc_now()),
        )
        conn.commit()
    finally:
        conn.close()


def load_trip_entries(db_path: Path) -> list[dict[str, str | None]]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "select entry_type, title, content, occurred_on, travel_day_id from trip_entries order by id"
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "entry_type": row[0],
            "title": row[1],
            "content": row[2],
            "occurred_on": row[3],
            "travel_day_id": row[4],
        }
        for row in rows
    ]


def load_final_reflections(db_path: Path) -> list[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("select content from final_reflections order by id").fetchall()
    finally:
        conn.close()
    return [row[0] for row in rows]


def follow_up_questions(base_dir: Path, trip_slug: str) -> list[str]:
    paths = require_workspace(base_dir, trip_slug)
    entries = load_trip_entries(paths["db"])
    have_types = {entry["entry_type"] for entry in entries}

    questions: list[str] = []
    for entry_type, question in QUESTION_RULES:
        if entry_type not in have_types:
            questions.append(question)
    return questions


def trip_checklist(base_dir: Path, trip_slug: str) -> list[str]:
    paths = require_workspace(base_dir, trip_slug)
    entries = load_trip_entries(paths["db"])
    have_types = {entry["entry_type"] for entry in entries}
    items: list[str] = []
    if "meal" not in have_types:
        items.append("Add at least one meal")
    if "fuel" not in have_types and "mileage" not in have_types:
        items.append("Add at least one fuel stop or mileage note")
    if "stop" not in have_types:
        items.append("Add a stop or attraction")
    if "campground" not in have_types:
        items.append("Add a campground review")
    if "travel" not in have_types:
        items.append("Add a travel-day note")
    reflections = load_final_reflections(paths["db"])
    if not reflections:
        items.append("Add a final reflection before finalizing the trip")
    return items


def trip_daily_summary(base_dir: Path, trip_slug: str, occurred_on: str) -> str:
    paths = require_workspace(base_dir, trip_slug)
    entries = [entry for entry in load_trip_entries(paths["db"]) if entry.get("occurred_on") == occurred_on]
    lines = [f"Daily summary for {occurred_on}", ""]
    if entries:
        lines.append("Captured today:")
        for entry in entries:
            lines.append(f"- {entry['title']}")
        lines.append("")
    else:
        lines.append("No structured entries recorded for this day yet.")
        lines.append("")

    have_types = {entry["entry_type"] for entry in entries}
    missing: list[str] = []
    if "meal" not in have_types:
        missing.append("Add at least one meal")
    if "fuel" not in have_types and "mileage" not in have_types:
        missing.append("Add at least one fuel stop or mileage note")
    if "stop" not in have_types:
        missing.append("Add a stop or attraction")
    if "campground" not in have_types:
        missing.append("Add a campground review")
    if "travel" not in have_types:
        missing.append("Add a travel-day note")
    if missing:
        lines.append("Still missing for this day:")
        for item in missing:
            lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def trip_capture_prompts(base_dir: Path, trip_slug: str, occurred_on: str | None = None) -> str:
    paths = require_workspace(base_dir, trip_slug)
    entries = load_trip_entries(paths["db"])
    if occurred_on:
        entries = [entry for entry in entries if entry.get("occurred_on") == occurred_on]
    have_types = {entry["entry_type"] for entry in entries}

    sections: list[tuple[str, str]] = []
    if "meal" not in have_types:
        sections.append(("Meals", "What did you eat today, and was any meal worth remembering in the binder?"))
    if "fuel" not in have_types and "mileage" not in have_types:
        sections.append(("Fuel & Mileage", "Did you buy fuel or notice anything important about mileage, grades, or fuel economy today?"))
    if "stop" not in have_types:
        sections.append(("Stops", "Were there any stops, attractions, viewpoints, or quick detours worth recording?"))
    if "campground" not in have_types:
        sections.append(("Campgrounds", "How was the campground in practice — site, hookups, noise, and would you return?"))
    if "travel" not in have_types:
        sections.append(("Travel Day", "What stood out about the drive today — weather, road conditions, delays, or lessons learned?"))

    lines = ["Capture prompts", ""]
    if occurred_on:
        lines[0] = f"Capture prompts for {occurred_on}"
    if not sections:
        lines.append("Nothing obvious is missing right now.")
        return "\n".join(lines) + "\n"
    for heading, prompt in sections:
        lines.append(f"## {heading}")
        lines.append(prompt)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_live_sections(db_path: Path) -> str:
    entries = load_trip_entries(db_path)
    if not entries:
        return ""

    grouped: dict[str, list[dict[str, str | None]]] = {}
    for entry in entries:
        section = SECTION_TITLES.get(entry["entry_type"] or "general", "General Notes")
        grouped.setdefault(section, []).append(entry)

    lines = [""]
    for section in ["Meals", "Stops", "Campgrounds", "Travel Notes", "Fuel & Mileage", "General Notes"]:
        section_entries = grouped.get(section, [])
        if not section_entries:
            continue
        lines.append(f"# {section}")
        lines.append("")
        for entry in section_entries:
            lines.append(f"## {entry['title']}")
            lines.append("")
            if entry.get("occurred_on"):
                lines.append(f"Date: {entry['occurred_on']}")
            if entry.get("travel_day_id"):
                lines.append(f"Travel day: {entry['travel_day_id']}")
            if entry.get("occurred_on") or entry.get("travel_day_id"):
                lines.append("")
            lines.append(entry["content"] or "")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_final_reflections(db_path: Path) -> str:
    reflections = load_final_reflections(db_path)
    if not reflections:
        return ""
    lines = ["", "# Final Reflections", ""]
    for reflection in reflections:
        lines.append(f"- {reflection}")
    lines.append("")
    return "\n".join(lines)


def render_live_sections_html(db_path: Path) -> str:
    entries = load_trip_entries(db_path)
    if not entries:
        return ""

    grouped: dict[str, list[dict[str, str | None]]] = {}
    for entry in entries:
        section = SECTION_TITLES.get(entry["entry_type"] or "general", "General Notes")
        grouped.setdefault(section, []).append(entry)

    bits = ["<section class=\"card\"><h2>Live Binder Updates</h2>"]
    for section in ["Meals", "Stops", "Campgrounds", "Travel Notes", "Fuel & Mileage", "General Notes"]:
        section_entries = grouped.get(section, [])
        if not section_entries:
            continue
        bits.append(f"<h3>{escape(section)}</h3>")
        for entry in section_entries:
            bits.append("<article class=\"live-entry\">")
            bits.append(f"<h4>{escape(entry.get('title') or '')}</h4>")
            if entry.get("occurred_on"):
                bits.append(f"<p><strong>Date:</strong> {escape(entry['occurred_on'] or '')}</p>")
            if entry.get("travel_day_id"):
                bits.append(f"<p><strong>Travel day:</strong> {escape(entry['travel_day_id'] or '')}</p>")
            content = escape(entry.get("content") or "").replace("\n", "<br>")
            bits.append(f"<p>{content}</p>")
            bits.append("</article>")
    bits.append("</section>")
    return "".join(bits)


def render_final_reflections_html(db_path: Path) -> str:
    reflections = load_final_reflections(db_path)
    if not reflections:
        return ""
    items = "".join(f"<li>{escape(reflection)}</li>" for reflection in reflections)
    return f"<section class=\"card\"><h2>Final Reflections</h2><ul>{items}</ul></section>"


def append_html_sections(base_html: str, *sections: str) -> str:
    extra = "".join(section for section in sections if section)
    if not extra:
        return base_html
    marker = "</body>"
    if marker in base_html:
        return base_html.replace(marker, extra + marker)
    return base_html + extra


def render_current_binder(base_dir: Path, trip_slug: str) -> Path:
    paths = require_workspace(base_dir, trip_slug)
    trip_data: dict[str, Any] = load_json(paths["trip_json"])
    binder = render_binder(trip_data)
    binder += render_live_sections(paths["db"])
    output_path = paths["output"] / "current-binder.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(binder, encoding="utf-8")
    return output_path


def render_current_binder_html(base_dir: Path, trip_slug: str) -> Path:
    paths = require_workspace(base_dir, trip_slug)
    trip_data: dict[str, Any] = load_json(paths["trip_json"])
    html = render_html(trip_data)
    html = append_html_sections(html, render_live_sections_html(paths["db"]))
    output_path = paths["output"] / "current-binder.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def finalize_trip(base_dir: Path, trip_slug: str) -> Path:
    paths = require_workspace(base_dir, trip_slug)
    trip_data: dict[str, Any] = load_json(paths["trip_json"])
    trip_data["status"] = "complete"
    paths["trip_json"].write_text(json.dumps(trip_data, indent=2) + "\n", encoding="utf-8")

    binder = render_binder(trip_data)
    binder += render_live_sections(paths["db"])
    binder += render_final_reflections(paths["db"])
    output_path = paths["output"] / "final-binder.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(binder, encoding="utf-8")
    return output_path


def render_final_binder_html(base_dir: Path, trip_slug: str) -> Path:
    paths = require_workspace(base_dir, trip_slug)
    trip_data: dict[str, Any] = load_json(paths["trip_json"])
    html = render_html(trip_data)
    html = append_html_sections(
        html,
        render_live_sections_html(paths["db"]),
        render_final_reflections_html(paths["db"]),
    )
    output_path = paths["output"] / "final-binder.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
