"""One-time load of data/seed/airports_seed.json into the airports table.

Dataset built from OurAirports (davidmegginson.github.io/ourairports-data),
filtered to airports with a valid 4-letter ICAO code and a type of
large/medium/small_airport or seaplane_base. Timezones computed via
timezonefinder. See data/seed/build_airports_seed.py and
memory/project_airports_import.md for the full process.
"""
import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Airport

DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"
DATA_PATH = Path(__file__).resolve().parent / "airports_seed.json"


def main() -> None:
    rows = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        existing = session.query(Airport).count()
        if existing:
            print(f"Skipping: airports table already has {existing} rows.")
            return
        for r in rows:
            session.add(
                Airport(
                    icao=r["icao"],
                    iata=r["iata"],
                    name=r["name"],
                    city=r["city"],
                    country=r["country"],
                    latitude=r["latitude"],
                    longitude=r["longitude"],
                    timezone=r["timezone"],
                )
            )
        session.commit()
    print(f"Loaded {len(rows)} airports into {DB_PATH}")


if __name__ == "__main__":
    main()
