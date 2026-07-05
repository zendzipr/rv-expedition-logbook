# Roadmap

## Sprint 1: Foundation

- Project overview and architecture documents
- Initial domain model
- Hermes skill
- Core JSON Schemas
- Binder Markdown templates
- Safe sample data
- Validation script

## Sprint 2: Domain depth

- Expand schemas
- Add provenance and confidence model
- Add deterministic rule checks
- Add more examples

## Sprint 2.1: Typed domain layer

- Add `Trip` and `TravelDay` Python domain objects
- Move derived trip totals and formatting helpers out of the renderer
- Refactor Markdown rendering to use the domain layer

## Sprint 1.5: First working renderer

- Generate a Markdown binder from `examples/sample-trip.json`
- Commit a sanitized generated example at `examples/sample-binder.md`
- Keep the renderer dependency-free for easy first use

## Sprint 3: Hermes workflow

- Refine capture flows
- Add follow-up question patterns
- Add import triage workflow
- Add private data handling guidance

## Sprint 4: Connectors

- RV Trip Wizard import mapping
- CSV import format
- GPX route import notes

## Sprint 5: Renderers

- Markdown binder generation
- HTML report generation
- PDF pipeline exploration

## Sprint 6: Analysis

- Fuel economy summaries
- Cost summaries
- Campground comparison
- Annual review reports

## Future

- Website
- Mobile companion
- Recommendation engine
- Knowledge graph storage
- Generalized expedition-logbook framework for sailing, overlanding, hiking, and other travel domains
