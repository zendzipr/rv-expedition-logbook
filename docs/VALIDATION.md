# Validation

RV Expedition Logbook validates data with JSON Schema Draft 2020-12 using the `jsonschema` Python package.

## Install

```bash
python3 -m pip install -e .
```

For local development in this environment, `uv` also works:

```bash
uv run python -m unittest discover -s tests
```

## Validate one file

```bash
python3 -m rv_logbook validate examples/sample-trip.json --schema trip
```

Supported schema names:

- `trip`
- `travel-day`
- `campground`
- `fuel-stop`
- `expense`
- `maintenance-event`
- `provenance`

## Validate the repository

```bash
python3 -m rv_logbook validate-repo
python3 scripts/validate.py
```

`validate-repo` checks that project schemas are valid JSON Schemas and that `examples/sample-trip.json` conforms to the Trip schema.

`scripts/validate.py` performs repository-level checks including schema validation, Hermes skill frontmatter checks, and binder template checks.
