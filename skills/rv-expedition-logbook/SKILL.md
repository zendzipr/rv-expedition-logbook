---
name: rv-expedition-logbook
description: Use when capturing, organizing, importing, analyzing, or generating RV trip logs, travel-day records, campground reviews, fuel and expense records, maintenance notes, and printable expedition binder pages.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [rv, travel, logbook, binder, schemas, trip-planning]
    related_skills: []
---

# RV Expedition Logbook

## Overview

Use this skill to help an RV traveler turn natural conversation, itinerary files, notes, and memories into structured RV travel knowledge.

The printable binder is one output. The source of truth is structured trip knowledge stored privately by the user, not committed to this repository.

## When to Use

Use this skill when the user asks to:

- record an RV trip, travel day, campground, fuel stop, expense, restaurant, attraction, or maintenance note
- import itinerary data from RV Trip Wizard, CSV, GPX, or similar tools
- generate a printable binder page, trip summary, annual review, or captain's log
- analyze RV travel history, costs, fuel economy, campgrounds, or lessons learned
- recommend future campgrounds, routes, or lower-stress travel plans based on prior records

Do not use this skill for generic vacation planning unless the output should be part of the RV expedition logbook.

## Core Principles

1. Conversation before forms.
2. Capture once, reuse everywhere.
3. Structured data is the source of truth.
4. Personal travel history belongs in Hermes/Hindsight or another private store.
5. GitHub contains reusable schemas, templates, docs, examples, and skill instructions.
6. AI extracts, summarizes, and recommends; deterministic code validates and computes.

## Capture Workflow

When the user gives an RV travel note:

1. Identify the likely object types: Trip, TravelDay, Campground, FuelStop, Expense, MaintenanceEvent, JournalEntry, Restaurant, or Attraction.
2. Extract obvious fields without asking redundant questions.
3. Preserve uncertainty instead of inventing details.
4. Ask only for missing fields that are needed for the user's requested output.
5. Attach provenance such as `conversation`, `rv-trip-wizard`, `csv`, `gpx`, `photo-metadata`, or `weather-import` when known.
6. Store private facts in the user's private knowledge system, not in the public repo.

## Capability Map

### Capture

- capture trip
- capture travel day
- capture campground stay or review
- capture fuel stop
- capture expense
- capture maintenance event
- capture restaurant or attraction
- capture lesson learned / captain's log

### Retrieve

- find trips, campgrounds, restaurants, attractions, and maintenance records
- answer questions about past stays, ratings, connectivity, costs, and route notes

### Analyze

- summarize expenses
- compute fuel economy when enough data exists
- compare campgrounds
- identify maintenance trends
- produce annual and lifetime statistics

### Generate

- printable binder pages
- trip summaries
- annual reviews
- captain's logs
- Markdown reports
- future HTML/PDF outputs

### Recommend

- campground candidates
- places to revisit
- lower-stress travel day plans
- maintenance follow-ups
- route or stop improvements

## Binder Generation Guidance

Binder pages should be generated from structured objects and templates, not manually maintained as the source of truth.

Initial binder pages:

- cover
- trip summary
- travel day dashboard
- campground review
- fuel log
- expense log
- maintenance log
- captain's log

## Template Map

Use the repository templates under `templates/binder/` as the canonical page layouts for binder outputs:

- `templates/binder/cover.md`
- `templates/binder/trip-summary.md`
- `templates/binder/travel-day-dashboard.md`
- `templates/binder/campground-review.md`
- `templates/binder/fuel-log.md`
- `templates/binder/expense-log.md`
- `templates/binder/maintenance-log.md`
- `templates/binder/captain-log.md`

When generating binder content:

1. Prefer structured trip data over handwritten markdown.
2. Map objects into the closest template instead of inventing a new page format.
3. Use trip-level templates for summaries and day-level templates for daily pages.
4. Keep markdown outputs aligned with the template headings and fields so later HTML/PDF rendering stays predictable.

## Tools and Commands

Use the project tooling instead of manual copy-paste when possible.

### Core validation and rendering

- `python3 scripts/validate.py` — validate repo assets and sample data
- `python3 -m rv_logbook validate <trip.json> --schema trip` — validate a trip JSON file
- `python3 -m rv_logbook render <trip.json> <output.md>` — render markdown binder
- `python3 -m rv_logbook render-html <trip.json> <output.html>` — render HTML binder/report

### Import and merge tools

- `python3 -m rv_logbook import-rtw <input.json> <output.json>` — normalize RV Trip Wizard export
- `python3 -m rv_logbook import-csv fuel-stop <input.csv> <output.json>`
- `python3 -m rv_logbook import-csv expense <input.csv> <output.json>`
- `python3 -m rv_logbook merge-records <record-type> <trip.json> <records.json> <output.json>`
- `python3 -m rv_logbook ingest-csv <csv-type> <trip.json> <input.csv> <output.json>`

### Live trip workspace tools

For binder-first operation during a real trip, use the live-trip commands in `rv_logbook.__main__`:

- `create-live-trip`
- `add-trip-note`
- `add-trip-entry`
- `add-meal`
- `add-fuel-stop`
- `add-stop`
- `add-campground-review`
- `add-travel-day-note`
- `add-mileage-note`
- `add-daily-review`
- `trip-checklist`
- `trip-daily-summary`
- `trip-capture-prompts`
- `trip-questions`
- `render-current-binder`
- `render-current-binder-html`
- `add-final-reflection`
- `finalize-trip`
- `render-final-binder-html`
- `trip-export-bundle`

If the user asks for the binder "as it stands right now," prefer the live-trip workspace commands over ad-hoc markdown editing.

## Import Guidance

RV Trip Wizard should be treated as a first-class future connector because it already contains structured itinerary data such as dates, routes, campgrounds, and distances.

Importers should map external data into the common domain model and preserve provenance. After import, ask only for information that cannot be imported, such as favorite memories, lessons learned, ratings, connectivity quality, and personal observations.

## Privacy Rules

Never commit real private travel records unless the user explicitly asks and the data is safe to publish.

Private data includes:

- exact personal location history
- private journals
- expenses
- reservation numbers
- photos with metadata
- campground reviews tied to private trips
- learned personal preferences

Use sanitized examples in the repository.

## Common Pitfalls

1. Treating the binder as the database. The binder is an output.
2. Asking the user to fill out long forms. Extract first, ask only for gaps.
3. Mixing reusable project files with private trip history.
4. Letting AI perform deterministic calculations without verification.
5. Designing the future mobile app before creating the first working schemas and templates.

## Verification Checklist

- [ ] Private trip data has not been committed to the repository.
- [ ] Structured objects match the schemas where schemas exist.
- [ ] Generated pages trace back to structured source objects.
- [ ] Missing or uncertain facts are marked clearly.
- [ ] Calculations are performed by deterministic code or verified explicitly.
