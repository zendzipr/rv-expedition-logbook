# RV Trip Wizard Connector Scaffold

The project now includes an initial RV Trip Wizard connector scaffold.

## Command

```bash
python3 -m rv_logbook import-rtw examples/sample-rtw-export.json output/rtw-trip.json
```

## Current supported scaffold shape

The connector currently accepts a simple JSON export shape:

```json
{
  "trip_name": "Blue Ridge Test Trip",
  "start_date": "2026-05-01",
  "end_date": "2026-05-03",
  "stops": [
    {
      "stop_id": "stop-001",
      "date": "2026-05-01",
      "name": "Sample Campground",
      "location": "Western North Carolina",
      "site": "12",
      "nightly_cost": 45.0,
      "distance_miles": 210,
      "route_notes": "Mountain grades required slower driving."
    }
  ]
}
```

## What it produces

A normalized trip JSON document with:

- trip `id`, `name`, `start_date`, `end_date`
- `travel_days`
- `campground` objects per stop
- campground expense records when `nightly_cost` is present
- `provenance.source = rv-trip-wizard`

## What it does not do yet

This is a scaffold, not a complete production connector.

It does not yet:

- parse unknown export variants automatically
- support CSV RTW export directly
- infer routes between stops
- import subjective ratings or memories
- merge directly into an existing trip without the separate merge step

## Why this exists

The point of this step is to establish a stable connector entrypoint and normalization contract so future RTW work extends a real module instead of starting from a blank page every time.
