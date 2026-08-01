# FS Career

A Microsoft Flight Simulator (2020/2024) career companion app: join an airline, fly real-world routes generated from a bundled dataset, get a flight plan pushed to SimBrief, deliver your own PA announcements over mic, and get scored on customer satisfaction (smoothness, timeliness, PA quality, comfort) instead of a traditional numeric pilot rating.

See [`.docs/OVERVIEW.md`](.docs/OVERVIEW.md) for the full design pitch, difficulty tiers, economy, reprimand system, and the ordered build roadmap.

## Status

Early build-out — data layer first. Currently done:

- SQLAlchemy models + Alembic migrations for the reference data (`airports`, `airlines`, `aircraft_families`, `aircraft`, `routes`) — see [`.docs/DATA_DICTIONARY.md`](.docs/DATA_DICTIONARY.md) and [`.docs/ERD.md`](.docs/ERD.md).
- Bundled dataset seeded into `data/fs_career.db`: 10,030 airports (OurAirports), 325+ airlines (Wikipedia), 179 aircraft variants across 48 families (ICAO 8643), 40,523 routes (OpenFlights), airline logos in `data/logos/`.
- An internal Tkinter-based DB admin tool (`.devtools/db_admin`) for browsing/editing seed data during development.

Not yet started: career profiles, SimConnect integration, hiring/route generation, SimBrief push/pull, PA capture, ambient audio, reprimands, economy, career progression UI. See the [ordered TODO list](.docs/OVERVIEW.md#ordered-todo-list) in the overview doc.

## Requirements

- Python >= 3.14
- Windows (SimConnect is Windows-only)
- [uv](https://docs.astral.sh/uv/) for dependency management

## Setup

```
uv sync
```

Apply migrations to create/update `data/fs_career.db`:

```
uv run alembic upgrade head
```

## Running

```
uv run run.py
```

## Dev tools

`.devtools/db_admin` is an internal GUI for browsing and editing the seed data tables directly (not part of the shipped app):

```
uv run run_admin.py
```

Dataset build/seed scripts live in `data/seed/` (one `build_*_seed.py` + `seed_*.py` pair per table, producing/consuming the `*_seed.json` files in that folder).
