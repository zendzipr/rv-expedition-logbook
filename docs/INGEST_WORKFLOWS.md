# Ingest CSV Workflow

The project now includes a higher-level workflow command that chains three steps:

1. import CSV
2. merge records into a trip JSON document
3. validate the merged trip against the Trip schema

## Command

```bash
python3 -m rv_logbook ingest-csv fuel-stop trip.json fuel-stops.csv output/merged-trip.json
```

## Replace mode

```bash
python3 -m rv_logbook ingest-csv expense trip.json expenses.csv output/merged-trip.json --merge-mode replace
```

## Why use this instead of separate commands

Use `ingest-csv` when you already know the source is CSV and the destination should be a validated trip JSON file.

Use the lower-level commands when you want to inspect or keep intermediate artifacts:

- `import-csv`
- `merge-records`
- `validate`

## Current supported ingest types

- `fuel-stop`
- `expense`
