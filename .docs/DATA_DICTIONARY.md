# Data Dictionary — Airlines & Routes

Covers the four core reference tables: `airports`, `airlines`, `aircraft`, `routes`. Models live in `models/`.

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
| `iata`     | String(2) | Yes      | Unique | IATA airline code, e.g. `BA`.                   |
| `name`     | String    | No       |        | Airline name, e.g. "British Airways".           |
| `callsign` | String    | No       |        | Radio callsign, e.g. "SPEEDBIRD".                |
| `country`  | String    | No       |        | Country the airline is based in.                 |

## `aircraft`

| Column         | Type      | Nullable | Key | Description                                        |
| -------------- | --------- | -------- | --- | --------------------------------------------------- |
| `icao_type`    | String(4) | No       | PK  | ICAO aircraft type designator, e.g. `B738`.          |
| `name`         | String    | No       |     | Aircraft name, e.g. "737-800".                       |
| `manufacturer` | String    | No       |     | Manufacturer, e.g. "Boeing".                          |

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

**Constraints:**
- `UNIQUE(airline_icao, flight_number)`
- `CHECK(distance_nm > 0)`
- `CHECK(duration_minutes > 0)`
- `CHECK(origin_icao != destination_icao)`

## Relationships

- `Airline.routes` ↔ `Route.airline` — one airline to many routes.
- `Aircraft.routes` ↔ `Route.aircraft` — one aircraft type to many routes.
- `Airport.departures` ↔ `Route.origin` — one airport to many routes departing from it.
- `Airport.arrivals` ↔ `Route.destination` — one airport to many routes arriving at it.

## Design notes

- Primary keys are the real-world codes themselves (not surrogate integers) for readability/debuggability when inspecting the dataset directly. The tradeoff: `routes` foreign keys store strings rather than small ints; `ON UPDATE CASCADE` is set on all three so correcting a code later propagates automatically. SQLite requires `PRAGMA foreign_keys=ON` per connection for this (and FK enforcement generally) to take effect — set this when engine/session setup is added.
- `routes` intentionally has a surrogate integer PK since no natural key exists at that granularity — a route is only unique once you have `(airline_icao, flight_number)`, which is enforced as a unique constraint rather than used as the PK directly, for a simpler single-column PK on the fact table.
- No frequency/schedule-days field: each service (flight number) is its own row rather than one row with a frequency count.
- Departure time is stored in UTC (not local) to avoid ambiguity/DST issues; convert to local using the origin airport's `timezone` when displaying.
- `airlines.prestige_tier` and `aircraft.category`/`aircraft.seats` are deliberately omitted for now — deferred pending future dataset editing.
