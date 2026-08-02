"""One-time load of data/seed/final_clean_airlines.json into the airlines table.

Dataset built from Wikipedia's "List of airline codes", filtered to airlines
without a defunct/disestablished category on their own article, then
cross-checked against IATA's official code-search registry to resolve
IATA-code conflicts (dropping non-current holders, keeping real controlled
duplicates). See memory/project_airline_import.md for the full process.
"""
import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Airline

DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"
DATA_PATH = Path(__file__).resolve().parent / "final_clean_airlines.json"


def main() -> None:
    rows = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        existing = session.query(Airline).count()
        if existing:
            print(f"Skipping: airlines table already has {existing} rows.")
            return
        for r in rows:
            session.add(
                Airline(
                    icao=r["icao"],
                    iata=r["iata"],
                    name=r["name"],
                    callsign=r["callsign"],
                    country=r["country"],
                )
            )
        session.commit()
    print(f"Loaded {len(rows)} airlines into {DB_PATH}")


if __name__ == "__main__":
    main()
