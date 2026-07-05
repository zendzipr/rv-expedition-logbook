# Architecture

## Summary

The project separates reusable binder machinery from private trip data.

```text
Traveler
  -> Conversation / Imports
  -> Hermes Skill
  -> Validation
  -> Domain Objects
  -> Per-trip workspace
  -> Binder renderers
  -> Current binder / Final binder
```

## Layers

| Layer | Responsibility | Location |
| --- | --- | --- |
| Conversation | Ask follow-up questions and capture trip details | Hermes |
| Import | Bring in RTW / CSV data | repository tools |
| Validation | Enforce deterministic rules and schemas | repository code |
| Domain | Normalize trip data and compute derived values | repository code |
| Workspace | Store per-trip evolving data and generated files | `data/trips/<trip-slug>/` |
| Rendering | Generate current and final binder outputs | repository templates/tools |

## AI versus deterministic code

AI should do AI-shaped work:

- ask for missing trip details
- summarize travel days
- help turn rough notes into readable binder text
- gather subjective details such as meals, stops, lessons, and campground impressions

Deterministic code should do deterministic work:

- validate schemas
- calculate totals, mileage, and fuel economy
- merge imported records into trips
- render binders predictably

## Data ownership

The repository is reusable and open-source friendly. Personal live trip data is private and should not be committed.

## Binder-first rule

The system should optimize for maintaining a useful trip binder during travel and producing a polished final binder afterward. Generic platform ambitions are secondary.
