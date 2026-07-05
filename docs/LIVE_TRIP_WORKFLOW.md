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

Render the current binder snapshot:

```bash
python3 -m rv_logbook render-current-binder blue-ridge-test --base-dir data
```

## Database

Each trip workspace includes a small SQLite database at `trip.db`.

Today it stores trip notes so the system can accumulate live-trip observations over time. It is intended to expand to other captured facts such as meals, comments, stop details, mileage context, and follow-up questions.

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

## Final binder

After the trip, the user should be able to:

- review the captured trip data
- add final reflections and lessons learned
- regenerate a polished **final binder**

## Design rule

When there is a trade-off between generic platform ideas and binder usability, prefer binder usability.
