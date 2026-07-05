# RV Expedition Logbook

RV Expedition Logbook is a binder-first RV trip system.

The primary job of the project is to help you maintain a **live trip binder during the trip** and then generate a **final trip binder after the trip** from the same structured data.

## What lives in this repository

This repository contains reusable project assets:

- Hermes skill instructions
- Domain documentation
- Typed Python domain objects
- JSON Schemas
- Markdown binder templates
- Example non-personal data
- Validation scripts and tests
- A binder-first live trip workflow

Personal travel history does **not** belong in this repository. Real trips, journals, ratings, expenses, and private notes belong in Hermes/Hindsight or another user-owned data store.

## Sprint 1 contents

```text
docs/                         project design documents
rv_logbook/                   Python package, CLI, domain objects, renderer, validation
data/trips/                   one folder per trip for evolving live-trip data
skills/rv-expedition-logbook/ Hermes skill and supporting references
schemas/                      JSON Schemas for core domain objects
templates/binder/             Markdown binder page templates
examples/                     safe sample data
scripts/                      validation tooling
tests/                        lightweight validation tests
```

## Core principle

Binder first. Keep one live trip workspace, update it as the trip unfolds, and generate the current binder snapshot or the final binder whenever needed.

A fuel stop, campground rating, travel-day note, maintenance event, meal, or reflection should be captured once and reused in the live binder and the final binder.

## Validate

Install the package in editable mode first:

```bash
python3 -m pip install -e .
```

Then run:

```bash
python3 scripts/validate.py
python3 -m rv_logbook validate examples/sample-trip.json --schema trip
python3 -m unittest discover -s tests
```

## Generate the sample binder

```bash
python3 -m rv_logbook render examples/sample-trip.json examples/sample-binder.md
```

The legacy script wrapper also works:

```bash
python3 scripts/render_binder.py examples/sample-trip.json examples/sample-binder.md
```

This reads the sanitized sample trip and renders a Markdown binder from the templates in `templates/binder/`.

## Generate the sample HTML report

```bash
python3 -m rv_logbook render-html examples/sample-trip.json examples/sample-report.html
```

This renders the same structured trip data as a standalone HTML report.

## Useful shortcuts

Common development tasks are available through `make`:

```bash
make validate
make test
make render-sample
make render-html-sample
make import-sample
make ingest-sample
make rtw-sample
```

## Live trip workspaces

The binder-first workflow now supports per-trip live workspaces under:

```text
data/trips/<trip-slug>/
```

Current live-trip commands include:

```bash
python3 -m rv_logbook create-live-trip <trip-slug> <rtw-export.json> --base-dir data
python3 -m rv_logbook add-trip-note <trip-slug> meal "Great BBQ in Asheville." --base-dir data
python3 -m rv_logbook add-trip-entry <trip-slug> meal "12 Bones Smokehouse" "Best ribs of the trip." --base-dir data
python3 -m rv_logbook add-trip-entry <trip-slug> fuel "Pilot fill-up" "Topped off before the climb." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-meal <trip-slug> "12 Bones Smokehouse" "Asheville, NC" "Best ribs of the trip." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-fuel-stop <trip-slug> Pilot "Asheville, NC" 42.5 165.75 12345 --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-stop <trip-slug> "Biltmore Estate" "Asheville, NC" "Great detour and worth the ticket price." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-campground-review <trip-slug> "Sample Campground" "Site 12" 4.5 yes "Quiet site, strong hookups, would gladly return." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-travel-day-note <trip-slug> "Rainy mountain driving" "Heavy fog and steep grades made the day slower than expected." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-mileage-note <trip-slug> "Mountain segment" 210 "Slow climbing miles with lower fuel economy than normal." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook add-daily-review <trip-slug> "Day 1 wrap-up" "Beautiful drive, good campground, and slower mountain miles than planned." --date 2026-05-01 --travel-day-id stop-001 --base-dir data
python3 -m rv_logbook trip-questions <trip-slug> --base-dir data
python3 -m rv_logbook trip-checklist <trip-slug> --base-dir data
python3 -m rv_logbook add-final-reflection <trip-slug> "Loved the Blue Ridge stretch and would stay longer next time." --base-dir data
python3 -m rv_logbook finalize-trip <trip-slug> --base-dir data
python3 -m rv_logbook render-current-binder <trip-slug> --base-dir data
```

These binder-native commands are there so you can capture what actually happened on the road without translating your trip into database jargon first.

See `docs/LIVE_TRIP_WORKFLOW.md` for the workspace layout and the live-trip workflow.

## Release notes

See `CHANGELOG.md` for milestone summaries.

## Continuous integration

GitHub Actions installs the package, runs JSON Schema validation, runs unit tests, renders the sample binder, renders the sample HTML report, exercises the sample CSV import path, exercises the RV Trip Wizard scaffold, verifies trip-record merging, and exercises the higher-level CSV ingest workflow on pushes and pull requests to `main`.

## Current milestone

The project can now produce a real artifact: a generated Markdown binder from structured trip JSON. That is the first working end-to-end slice of the system.
