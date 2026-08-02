"""One-time load of data/seed/aircraft_seed.json into aircraft_families/aircraft.

Family/variant list curated from ICAO Doc 8643 (aircraft type designators),
scoped to types with real-world airline/commercial service and a plausible
MSFS presence (default or freeware/payware addon) - see
memory/project_aircraft_import.md for the full process.
"""
import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Aircraft, AircraftFamily

DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"
DATA_PATH = Path(__file__).resolve().parent / "aircraft_seed.json"


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        existing = session.query(AircraftFamily).count()
        if existing:
            print(f"Skipping: aircraft_families table already has {existing} rows.")
            return

        family_ids = {}
        for f in data["families"]:
            family = AircraftFamily(
                name=f["name"], manufacturer=f["manufacturer"], category=f["category"]
            )
            session.add(family)
            session.flush()
            family_ids[f["name"]] = family.id

        for a in data["aircraft"]:
            session.add(
                Aircraft(
                    icao_type=a["icao_type"],
                    name=a["name"],
                    family_id=family_ids[a["family"]],
                )
            )
        session.commit()
    print(f"Loaded {len(data['families'])} families, {len(data['aircraft'])} aircraft into {DB_PATH}")


if __name__ == "__main__":
    main()
