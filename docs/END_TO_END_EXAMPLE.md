# End-to-End Example

This document shows a realistic sample pipeline using the current project machinery.

## 1. Validate the repository

```bash
make validate
make test
```

## 2. Import CSV data into normalized JSON

```bash
python3 -m rv_logbook import-csv fuel-stop examples/sample-fuel-stops.csv output/fuel-stops.json
python3 -m rv_logbook import-csv expense examples/sample-expenses.csv output/expenses.json
```

## 3. Merge imported records into a trip

```bash
python3 -m rv_logbook merge-records fuel-stop examples/sample-trip.json examples/sample-fuel-stops-merge.json output/merged-trip.json
python3 -m rv_logbook validate output/merged-trip.json --schema trip
```

## 4. Use the higher-level ingest workflow instead

```bash
python3 -m rv_logbook ingest-csv fuel-stop examples/sample-trip.json examples/sample-fuel-stops-single.csv output/ingested-trip.json
python3 -m rv_logbook validate output/ingested-trip.json --schema trip
```

## 5. Render outputs

```bash
python3 -m rv_logbook render output/ingested-trip.json output/ingested-binder.md
python3 -m rv_logbook render-html output/ingested-trip.json output/ingested-report.html
```

## 6. Optional RV Trip Wizard scaffold path

```bash
python3 -m rv_logbook import-rtw examples/sample-rtw-export.json output/rtw-trip.json
python3 -m rv_logbook render output/rtw-trip.json output/rtw-binder.md
python3 -m rv_logbook render-html output/rtw-trip.json output/rtw-report.html
```

## Expected artifacts

After the pipeline runs, you should have:

- `output/fuel-stops.json`
- `output/expenses.json`
- `output/merged-trip.json`
- `output/ingested-trip.json`
- `output/ingested-binder.md`
- `output/ingested-report.html`
- optionally `output/rtw-trip.json`

This is enough to prove the repository is operating as a workflow system rather than a decorative filing cabinet.
