# RV Trip Wizard Import Notes

RV Trip Wizard is a planned first-class connector.

Expected imported fields may include:

- trip name
- dates
- stop sequence
- campground names
- addresses or coordinates
- estimated distances
- route notes
- reservation notes if exported by the user

Import rules:

1. Preserve the original source field names where practical.
2. Map imported data into Trip, TravelDay, Campground, Route, and Waypoint objects.
3. Mark imported facts with `provenance.source = rv-trip-wizard`.
4. Do not assume imported data is correct; allow correction events or edited records.
5. After import, ask for subjective data: ratings, memories, lessons, connectivity quality, and would-return decisions.
