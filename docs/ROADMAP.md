# Roadmap

## Step 1: Foundation

- Project overview and architecture documents
- Initial domain model
- Hermes skill
- Core JSON Schemas
- Binder Markdown templates
- Safe sample data
- Validation script

## Step 2: Domain depth

- Expand schemas
- Add provenance and confidence model
- Add deterministic rule checks
- Add more examples

## Step 2.1: Typed domain layer

- Add `Trip` and `TravelDay` Python domain objects
- Move derived trip totals and formatting helpers out of the renderer
- Refactor Markdown rendering to use the domain layer

## Step 3: Import and merge workflows

- CSV import for fuel stops and expenses
- Merge imported records into trips
- Add append/replace merge modes
- Add higher-level ingest workflow
- Add RV Trip Wizard connector scaffold

## Step 4: Multi-format binder output

- Markdown binder generation
- HTML report generation
- Sample generated artifacts

## Step 5: Live trip workflow

- Per-trip workspace under `data/trips/`
- Current binder snapshot generation during travel
- Final binder generation after travel
- Question-driven enrichment of imported trip data

## Later

- richer RV Trip Wizard format support
- PDF output if needed
- stronger trip-editing UX
- optional stats and reporting only where they directly help the binder
