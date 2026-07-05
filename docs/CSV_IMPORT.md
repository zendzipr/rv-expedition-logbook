# CSV Import

The project now includes a first importer foundation for simple structured CSV files.

## Supported import types

### Fuel stops

```bash
python3 -m rv_logbook import-csv fuel-stop examples/sample-fuel-stops.csv output/fuel-stops.json
```

Expected columns:

- `id`
- `travel_day_id`
- `date`
- `vendor`
- `location`
- `odometer`
- `gallons`
- `total_cost`
- `price_per_gallon`
- `notes`

### Expenses

```bash
python3 -m rv_logbook import-csv expense examples/sample-expenses.csv output/expenses.json
```

Expected columns:

- `id`
- `travel_day_id`
- `date`
- `category`
- `amount`
- `vendor`
- `notes`

## Behavior

- Required columns are enforced.
- Numeric fields are converted to numbers.
- Output is normalized JSON.
- Import currently targets individual record arrays, not full trip-merging yet.

## Why CSV first

CSV is a simple connector that establishes importer patterns before adding more peculiar sources such as RV Trip Wizard exports.
