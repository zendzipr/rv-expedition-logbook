# Domain Objects

The project now has a typed Python domain layer in `rv_logbook/domain.py`.

The domain layer does not replace JSON Schemas. Schemas define the external data contract. Domain objects provide a normalized in-code representation with derived values for renderers, importers, and analysis.

## Current objects

### `Trip`

Created from a trip JSON object:

```python
from rv_logbook.domain import Trip

trip = Trip.from_dict(data)
```

Useful properties:

- `trip.travel_days`
- `trip.total_miles`
- `trip.campground_count`
- `trip.fuel_stops`
- `trip.expenses`
- `trip.maintenance_events`
- `trip.total_fuel_cost`
- `trip.total_expense_cost`
- `trip.total_maintenance_cost`
- `trip.total_cost`
- `trip.highlights`
- `trip.lessons_learned`

For rendering:

```python
context = trip.to_template_context()
```

### `TravelDay`

Created from a travel-day JSON object:

```python
from rv_logbook.domain import TravelDay

day = TravelDay.from_dict(data)
```

Useful properties:

- `day.miles`
- `day.campground`
- `day.highlights`
- `day.lessons_learned`
- `day.fuel_stops`
- `day.expenses`
- `day.maintenance_events`
- `day.drive_time`

For rendering:

```python
context = day.to_template_context()
```

## Why this matters

The renderer no longer computes trip totals directly from loose dictionaries. It now asks the domain layer for normalized facts. That gives future importers and renderers a stable place to put business rules.

The database knows. The database always knows. But the domain layer now has a map to where the bodies are buried.
