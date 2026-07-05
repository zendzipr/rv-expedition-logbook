# Domain Model

## Design goal

Use a small, stable vocabulary for RV travel records. Capture information once as domain objects, then render or analyze it many ways.

## Core objects

### Trip

A named journey with a start date, end date, travelers, vehicle context, and a collection of travel days.

### TravelDay

A day of movement or travel activity. Usually belongs to a trip and may include route notes, distance, fuel stops, expenses, campground arrival, weather, and journal entries.

### Campground

A place where the RV stayed or may stay. Includes location, site details, hookups, amenities, connectivity, rating, and notes.

### FuelStop

A fuel purchase or charging stop. Includes date, location, odometer, gallons, total cost, price per gallon, and notes.

### Expense

A cost associated with a trip or travel day. Includes category, amount, date, vendor, payment method, and notes.

### MaintenanceEvent

A repair, inspection, service, or equipment issue. Includes date, vehicle/equipment, odometer if relevant, cost, severity, and follow-up needs.

### JournalEntry

Narrative memory, captain's log entry, lesson learned, or personal observation.

## Supporting concepts

- Route
- Waypoint
- Campsite
- Hookup
- Amenity
- Restaurant
- Attraction
- Trail
- NationalPark
- StatePark
- WeatherObservation
- RoadCondition
- Favorite
- Recommendation
- Preference

## Relationships

```text
Trip
  -> TravelDay
       -> Route / Waypoint
       -> Campground
       -> FuelStop
       -> Expense
       -> MaintenanceEvent
       -> JournalEntry
       -> Restaurant / Attraction
```

## Rules

Initial deterministic rules:

- `Trip` requires `id`, `name`, and `start_date`.
- `TravelDay` requires `id`, `trip_id`, and `date`.
- `FuelStop` requires `id`, `date`, and either gallons/cost data or a note explaining missing data.
- `Expense` requires `id`, `date`, `category`, and `amount`.
- `MaintenanceEvent` requires `id`, `date`, `title`, and `status`.
- Personal/private records should not be committed to the repository except sanitized examples.
