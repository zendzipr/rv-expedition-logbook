"""Live trip workspace helpers for binder-first trip management."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .render import load_json, render_binder
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


def add_trip_note(base_dir: Path, trip_slug: str, note_type: str, content: str) -> Path:
    if note_type not in NOTE_FILES:
        valid = ", ".join(sorted(NOTE_FILES))
        raise LiveTripError(f"unknown note type '{note_type}'. Valid types: {valid}")
    paths = trip_paths(base_dir, trip_slug)
    if not paths["trip_json"].exists():
        raise LiveTripError(f"trip workspace not found: {trip_slug}")
    init_trip_db(paths["db"])

    timestamp = datetime.now(timezone.utc).isoformat()
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


def render_current_binder(base_dir: Path, trip_slug: str) -> Path:
    paths = trip_paths(base_dir, trip_slug)
    if not paths["trip_json"].exists():
        raise LiveTripError(f"trip workspace not found: {trip_slug}")
    trip_data: dict[str, Any] = load_json(paths["trip_json"])
    binder = render_binder(trip_data)
    output_path = paths["output"] / "current-binder.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(binder, encoding="utf-8")
    return output_path
