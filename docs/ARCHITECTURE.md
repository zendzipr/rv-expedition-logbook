# Architecture

## Summary

The project separates reusable framework assets from personal travel data.

```text
Traveler
  -> Conversation / Imports
  -> Hermes Skill
  -> Extraction
  -> Validation
  -> Domain Objects
  -> Private Knowledge Store
  -> Renderers
  -> Outputs
```

## Layers

| Layer | Responsibility | Location |
| --- | --- | --- |
| Conversation | Natural capture and follow-up questions | Hermes |
| Extraction | Convert notes into structured objects | Hermes / tools |
| Validation | Enforce deterministic rules and schemas | repository code |
| Knowledge | Private trip records and learned preferences | Hermes/Hindsight |
| Rendering | Generate binder/report/HTML output | repository templates/tools |

## AI versus deterministic code

AI should do AI-shaped work:

- extract structured information from conversation
- summarize travel days and trips
- recommend places, routes, and follow-ups
- generate readable narrative

Deterministic code should do deterministic work:

- validate schemas
- calculate totals, mileage, and fuel economy
- enforce required fields
- render templates predictably
- preserve provenance

## Data ownership

The repository is reusable and open-source friendly. Personal travel data is private and should not be committed.

## Provenance

Every important fact should eventually carry provenance:

- source type, such as conversation, RV Trip Wizard, GPX, CSV, photo metadata, or weather import
- source reference, where safe
- captured timestamp
- confidence level for AI-extracted facts

## Future architecture

The same domain layer should eventually support multiple interfaces:

- Hermes conversation
- voice
- mobile
- website
- API
- printable binder

Hermes is one interface, not the whole system.
