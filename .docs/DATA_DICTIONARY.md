# Data Dictionary — Airlines & Routes

Covers the core reference tables: `airports`, `airlines`, `aircraft_families`, `aircraft`, `routes`. Models live in `models/`.

## `airports`

| Column      | Type       | Nullable | Key      | Description                                           |
| ----------- | ---------- | -------- | -------- | ------------------------------------------------------ |
| `icao`      | String(4)  | No       | PK       | ICAO airport code, e.g. `EGLL`.                        |
| `iata`      | String(3)  | Yes      | Unique   | IATA airport code, e.g. `LHR`. Not all airports have one. |
| `name`      | String     | No       |          | Airport name.                                          |
| `city`      | String     | No       |          | City the airport serves.                                |
| `country`   | String     | No       |          | Country the airport is in.                              |
| `latitude`  | Float      | No       |          | Decimal degrees.                                        |
| `longitude` | Float      | No       |          | Decimal degrees.                                        |
| `timezone`  | String     | No       |          | IANA timezone name (e.g. `Europe/London`), used to convert `routes.departure_time_utc` to local time for display/PA scheduling. |

## `airlines`

| Column     | Type      | Nullable | Key    | Description                                    |
| ---------- | --------- | -------- | ------ | ----------------------------------------------- |
| `icao`     | String(3) | No       | PK     | ICAO airline code, e.g. `BAW`.                  |
| `iata`     | String(2) | Yes      | Indexed | IATA airline code, e.g. `BA`. Not unique — IATA permits "controlled duplicates," the same code assigned to more than one airline at once when there's no risk of confusion (e.g. separate regional markets). |
| `name`     | String    | No       |        | Airline name, e.g. "British Airways".           |
| `callsign` | String    | No       |        | Radio callsign, e.g. "SPEEDBIRD".                |
| `country`  | String    | No       |        | Country the airline is based in.                 |
| `has_logo` | Boolean   | No       | Default `False` | Whether a logo file exists at `data/logos/{icao}.png`. Logos aren't stored in the DB (BLOB) to keep `fs_career.db` small — see design notes. |

## `aircraft_families`

Groups variant-level `aircraft` rows by real-world type-rating grain (e.g. all 737 NG/MAX variants share one family), and doubles as the manufacturer/category lookup.

| Column         | Type    | Nullable | Key      | Description                                                                 |
| -------------- | ------- | -------- | -------- | ---------------------------------------------------------------------------- |
| `id`           | Integer | No       | PK       | Autoincrement; no natural key at the family grain.                          |
| `name`         | String  | No       | Unique   | Family name, e.g. "Boeing 737", "Cessna Citation".                          |
| `manufacturer` | String  | No       |          | Manufacturer, e.g. "Boeing".                                                  |
| `category`     | String  | No       | Check    | One of `mainline_jet`, `regional_jet`, `turboprop`, `business`. `business` covers both business jets and business turboprops (King Air, TBM, Pilatus) since the grouping reflects market segment, not propulsion. |

## `aircraft`

| Column         | Type      | Nullable | Key                        | Description                                        |
| -------------- | --------- | -------- | -------------------------- | --------------------------------------------------- |
| `icao_type`    | String(4) | No       | PK                          | ICAO aircraft type designator, e.g. `B738`.          |
| `name`         | String    | No       |                             | Variant name, e.g. "737-800".                        |
| `family_id`    | Integer   | No       | FK → `aircraft_families.id` | Family this variant belongs to.                      |

## `routes`

The fact table — each row is one specific scheduled service: an airline flying a given flight number, on a given aircraft type, between two airports, departing at a given local time.

| Column                  | Type      | Nullable | Key                          | Description                                                              |
| ------------------------ | --------- | -------- | ----------------------------- | -------------------------------------------------------------------------- |
| `id`                     | Integer   | No       | PK (surrogate)                | Autoincrement; `routes` has no natural key of its own.                     |
| `airline_icao`           | String(3) | No       | FK → `airlines.icao`          | Operating airline. `ON UPDATE CASCADE`.                                    |
| `origin_icao`            | String(4) | No       | FK → `airports.icao`          | Departure airport. `ON UPDATE CASCADE`.                                    |
| `destination_icao`       | String(4) | No       | FK → `airports.icao`          | Arrival airport. `ON UPDATE CASCADE`.                                      |
| `aircraft_icao_type`     | String(4) | No       | FK → `aircraft.icao_type`     | Aircraft type operating this service. `ON UPDATE CASCADE`.                 |
| `flight_number`          | String    | No       | Unique with `airline_icao`    | e.g. `117`. Unique per airline — no two simultaneous services share one.  |
| `distance_nm`            | Float     | No       |                                | Great-circle distance in nautical miles, stored (not computed on read).    |
| `departure_time_utc`     | Time      | No       |                                | Scheduled departure time at `origin`, in UTC, rounded to the nearest 5 minutes at import time (not DB-enforced). |
| `duration_minutes`       | Integer   | No       |                                | Scheduled flight duration in minutes, rounded to the nearest 5 minutes at import time (not DB-enforced). |
| `flight_number_synthetic` | Boolean  | No       | Default `True`                | `True` if `flight_number` was generated rather than sourced from a real airline flight number. |
| `schedule_synthetic`     | Boolean   | No       | Default `True`                | `True` if `departure_time_utc`/`duration_minutes` were generated rather than sourced from a real timetable. |
| `aircraft_icao_type_synthetic` | Boolean | No  | Default `False`               | `True` if `aircraft_icao_type` was guessed from a generic/unmatched OpenFlights equipment code (e.g. `"737"` instead of `"738"`) rather than a real reported variant. |

**Constraints:**
- `UNIQUE(airline_icao, flight_number)`
- `CHECK(distance_nm > 0)`
- `CHECK(duration_minutes > 0)`
- `CHECK(origin_icao != destination_icao)`

## Relationships

- `Airline.routes` ↔ `Route.airline` — one airline to many routes.
- `Aircraft.routes` ↔ `Route.aircraft` — one aircraft type to many routes.
- `AircraftFamily.aircraft` ↔ `Aircraft.family` — one family to many variants.
- `Airport.departures` ↔ `Route.origin` — one airport to many routes departing from it.
- `Airport.arrivals` ↔ `Route.destination` — one airport to many routes arriving at it.

## Design notes

- Primary keys are the real-world codes themselves (not surrogate integers) for readability/debuggability when inspecting the dataset directly. The tradeoff: `routes` foreign keys store strings rather than small ints; `ON UPDATE CASCADE` is set on all three so correcting a code later propagates automatically. SQLite requires `PRAGMA foreign_keys=ON` per connection for this (and FK enforcement generally) to take effect — set this when engine/session setup is added.
- `routes` intentionally has a surrogate integer PK since no natural key exists at that granularity — a route is only unique once you have `(airline_icao, flight_number)`, which is enforced as a unique constraint rather than used as the PK directly, for a simpler single-column PK on the fact table.
- No frequency/schedule-days field: each service (flight number) is its own row rather than one row with a frequency count.
- Departure time is stored in UTC (not local) to avoid ambiguity/DST issues; convert to local using the origin airport's `timezone` when displaying.
- `airlines.prestige_tier` and `aircraft.seats` are deliberately omitted for now — deferred pending future dataset editing.
- `aircraft_families` was added instead of putting `category`/`manufacturer` directly on `aircraft` because real-world type ratings are earned per family (e.g. one 737 rating covers all NG/MAX variants), not per exact variant — the type-rating system planned in the roadmap should key off `family_id`, not `icao_type`, once it's built.
- The seed dataset (`data/seed/aircraft_seed.json`) is scoped to aircraft with real-world airline/business service *and* a plausible MSFS presence (default or addon) — see `memory/project_aircraft_import.md`.
- `airports` is seeded from OurAirports, filtered to a valid 4-letter ICAO code (`icao_code` column, all letters) and excluding `heliport`/`balloonport`/`closed` types — see `memory/project_airports_import.md` for why this filter is a reasonable proxy for "servable by mainline/regional/business aviation" rather than a size cutoff. `timezone` isn't in the source data and is computed from lat/lon via `timezonefinder` at build time.
- `airlines.has_logo`/`data/logos/`: logos are downloaded from Kiwi.com's public airline-logo CDN, keyed by IATA code, for the 325 airlines that have at least one route (route-less airlines — ~400 of them — are out of scope). 316/325 resolved; the remaining 9 are low-route (≤44) airlines with either no IATA code or no artwork on the CDN, and were left unresolved. See `data/seed/fetch_airline_logos.py` and `memory/project_airline_logos.md`.
- `routes` is bulk-seeded from OpenFlights' route network data (real airline → route → aircraft-type triples), matched against our own `airlines`/`airports`/`aircraft` tables — airlines/airports we don't have are dropped, but unmatched/generic equipment codes (e.g. KLM's rows mostly saying `"330"`/`"737"` instead of a real variant code) fall back to a representative variant from our `aircraft` table rather than being dropped, flagged via `aircraft_icao_type_synthetic`. `flight_number`, `departure_time_utc`, and `duration_minutes` are always synthesized, since no free source has bulk real-world schedule data (that's commercial OAG/Cirium territory) — see `memory/project_routes_import.md` for the full process and coverage numbers.

### Known gaps

- **BA Euroflyer** (Gatwick-based BA short-haul subsidiary, ICAO `EFW`, callsign "EUROFLYER") is missing from `airlines` — it didn't come through the Wikipedia "List of airline codes" pull. BA CityFlyer (`CFE`) did get picked up correctly as its own row, so Euroflyer should follow the same pattern if added later. Adding it properly also means sourcing its own routes rather than leaving it route-less, which hasn't been done.
