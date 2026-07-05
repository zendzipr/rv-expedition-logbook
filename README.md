# RV Expedition Logbook

RV Expedition Logbook is a knowledge-first RV travel logging system.

It is not just a printable binder. The binder is one generated output from a structured travel knowledge model that can also produce Markdown reports, HTML pages, dashboards, statistics, and future mobile or web experiences.

## What lives in this repository

This repository contains reusable project assets:

- Hermes skill instructions
- Domain documentation
- Typed Python domain objects
- JSON Schemas
- Markdown binder templates
- Example non-personal data
- Validation scripts and tests

Personal travel history does **not** belong in this repository. Real trips, journals, ratings, expenses, and private notes belong in Hermes/Hindsight or another user-owned data store.

## Sprint 1 contents

```text
docs/                         project design documents
rv_logbook/                   Python package, CLI, domain objects, renderer, validation
skills/rv-expedition-logbook/ Hermes skill and supporting references
schemas/                      JSON Schemas for core domain objects
templates/binder/             Markdown binder page templates
examples/                     safe sample data
scripts/                      validation tooling
tests/                        lightweight validation tests
```

## Core principle

Capture once. Reuse everywhere.

A fuel stop, campground rating, travel-day note, or maintenance event should be captured once as structured knowledge and then reused in binders, reports, statistics, recommendations, and future interfaces.

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

## Release notes

See `CHANGELOG.md` for milestone summaries.

## Continuous integration

GitHub Actions installs the package, runs JSON Schema validation, runs unit tests, renders the sample binder, renders the sample HTML report, exercises the sample CSV import path, exercises the RV Trip Wizard scaffold, verifies trip-record merging, and exercises the higher-level CSV ingest workflow on pushes and pull requests to `main`.

## Current milestone

The project can now produce a real artifact: a generated Markdown binder from structured trip JSON. That is the first working end-to-end slice of the system.
