"""One-time load of data/seed/routes_seed.json into the routes table.

Built from OpenFlights' route network data, matched against our own
airlines/airports/aircraft tables, with flight numbers/durations
synthesized (no free bulk source has real schedules) - see
data/seed/build_routes_seed.py and memory/project_routes_import.md for the
full process.
"""
import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Route

DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"
DATA_PATH = Path(__file__).resolve().parent / "routes_seed.json"


def main() -> None:
    rows = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        existing = session.query(Route).count()
        if existing:
            print(f"Skipping: routes table already has {existing} rows.")
            return
        for r in rows:
            session.add(
                Route(
                    airline_icao=r["airline_icao"],
                    origin_icao=r["origin_icao"],
                    destination_icao=r["destination_icao"],
                    aircraft_icao_type=r["aircraft_icao_type"],
                    flight_number=r["flight_number"],
                    distance_nm=r["distance_nm"],
                    duration_minutes=r["duration_minutes"],
                    flight_number_synthetic=r.get("flight_number_synthetic", True),
                    schedule_synthetic=r.get("schedule_synthetic", True),
                    aircraft_icao_type_synthetic=r.get("aircraft_icao_type_synthetic", False),
                )
            )
        session.commit()
    print(f"Loaded {len(rows)} routes into {DB_PATH}")


if __name__ == "__main__":
    main()
