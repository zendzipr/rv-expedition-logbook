## v0.1.0 — Foundation release

This release turns the project from a planning scaffold into a working, installable pipeline.

### Added

- installable Python package with `pyproject.toml`
- `rv-logbook` CLI entry point
- JSON Schema validation for core project objects
- typed Python domain objects for `Trip` and `TravelDay`
- Markdown binder rendering
- HTML report rendering
- CSV import foundation for `fuel-stop` and `expense`
- duplicate-aware trip merge workflow with append/replace modes
- RV Trip Wizard connector scaffold
- higher-level CSV ingest workflow
- GitHub Actions CI coverage for validation, tests, imports, rendering, and merge workflows
- sample sanitized artifacts and example source files

### Highlights

- installable Python package
- Markdown and HTML rendering from the same structured trip data
- schema validation and domain modeling
- connector scaffolding for CSV and RV Trip Wizard
- reusable workflow commands instead of isolated scripts

### Notes

This is a pragmatic v0.1.0 milestone, not a finished v1.0 product. The machinery now works end-to-end for sample data, which is generally considered a better starting point than inspirational folder names.
