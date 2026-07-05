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
  notes/
    daily-notes.md
    campground-notes.md
    meal-notes.md
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
