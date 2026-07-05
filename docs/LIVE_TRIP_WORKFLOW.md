# Live Trip Workflow

The project is now framed around a binder-first workflow.

## Goal

Support two states of the same trip binder:

1. **Current binder snapshot** during the trip
2. **Final binder** after the trip

## Per-trip workspace

Each trip should live in its own folder under:

```text
data/trips/<trip-slug>/
```

Recommended structure:

```text
data/trips/<trip-slug>/
  trip.json
  trip.db
  notes/
    daily-notes.md
    campground-notes.md
    meal-notes.md
    travel-notes.md
    stop-notes.md
    general-notes.md
  imports/
    rtw-export.json
    fuel-stops.csv
    expenses.csv
  output/
    current-binder.md
    current-binder.html
    final-binder.md
    final-binder.html
```

## Current commands

Create a live trip workspace from an RV Trip Wizard export:

```bash
python3 -m rv_logbook create-live-trip blue-ridge-test examples/sample-rtw-export.json --base-dir data
```

Add a note during the trip:

```bash
python3 -m rv_logbook add-trip-note blue-ridge-test meal "Great BBQ in Asheville." --base-dir data
```

Add a structured entry that should appear in the live binder snapshot:

```bash
python3 -m rv_logbook add-trip-entry blue-ridge-test meal "12 Bones Smokehouse" "Best ribs of the trip." --base-dir data
```

Structured entries can also be tied to a date and a travel day:

```bash
python3 -m rv_logbook add-trip-entry blue-ridge-test fuel "Pilot fill-up" "Topped off before the climb." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
```

If you do not want to think in generic entry types, you can use binder-native helpers:

```bash
python3 -m rv_logbook add-meal blue-ridge-test "12 Bones Smokehouse" "Asheville, NC" "Best ribs of the trip." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-fuel-stop blue-ridge-test Pilot "Asheville, NC" 42.5 165.75 12345 --date 2026-05-01 --travel-day-id stop-001 --base-dir data
```

List follow-up questions the system still wants answered:

```bash
python3 -m rv_logbook trip-questions blue-ridge-test --base-dir data
```

Add a final reflection after the trip:

```bash
python3 -m rv_logbook add-final-reflection blue-ridge-test "Loved the Blue Ridge stretch and would stay longer next time." --base-dir data
```

Finalize the trip and generate the final binder:

```bash
python3 -m rv_logbook finalize-trip blue-ridge-test --base-dir data
```

Render the current binder snapshot:

```bash
python3 -m rv_logbook render-current-binder blue-ridge-test --base-dir data
```

## Database

Each trip workspace includes a small SQLite database at `trip.db`.

Today it stores:

- trip notes
- structured trip entries
- final reflections

Structured entries can carry binder-friendly metadata like an entry date and a related `travel_day_id`, so meals, fuel stops, mileage context, and stop commentary can be tied back to the right part of the trip.

## Live trip binder

During the trip, the user should be able to:

- import RV Trip Wizard data
- add fuel stops
- add expenses
- add campground notes
- add mileage notes
- add meals and stop commentary
- answer follow-up questions about the trip
- regenerate the **current binder snapshot** at any time
- capture structured sections such as meals, stops, campgrounds, travel notes, and fuel or mileage context

## Final binder

After the trip, the user should be able to:

- review the captured trip data
- add final reflections and lessons learned
- regenerate a polished **final binder**

## Design rule

When there is a trade-off between generic platform ideas and binder usability, prefer binder usability.
