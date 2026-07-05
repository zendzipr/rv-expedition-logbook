# Trip Merge Workflow

Imported records become genuinely useful when they can be attached to a trip without hand-editing JSON.

## Merge normalized records into a trip

```bash
python3 -m rv_logbook merge-records fuel-stop \
  examples/sample-trip.json \
  examples/sample-fuel-stops-merge.json \
  output/merged-trip.json
```

Supported record types:

- `fuel-stop`
- `expense`

## Behavior

- Records are matched by `travel_day_id`.
- Matching records are appended to the target travel day's array by default.
- `--mode replace` replaces the target travel day's existing record array instead of appending.
- Append mode rejects duplicate record IDs already present on the target travel day.
- Existing trip fields are preserved.
- Unknown `travel_day_id` values fail fast.

## Typical pipeline

1. Import CSV into normalized JSON:

```bash
python3 -m rv_logbook import-csv fuel-stop examples/sample-fuel-stops.csv output/fuel-stops.json
```

2. Merge compatible imported records into a trip JSON document:

```bash
python3 -m rv_logbook merge-records fuel-stop trip.json output/fuel-stops.json output/merged-trip.json
```

Replace mode is also available:

```bash
python3 -m rv_logbook merge-records fuel-stop trip.json output/fuel-stops.json output/merged-trip.json --mode replace
```

3. Validate and render:

```bash
python3 -m rv_logbook validate output/merged-trip.json --schema trip
python3 -m rv_logbook render output/merged-trip.json output/merged-binder.md
```
