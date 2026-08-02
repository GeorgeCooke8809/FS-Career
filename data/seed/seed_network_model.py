"""Populate airlines.network_model for airlines that have seeded routes.

Classification ('hub_and_spoke' vs 'point_to_point') is real-world research
on each carrier's route network structure, stored in network_model.json.
Airlines without routes are left NULL — see memory/project_network_model.md.
"""
import json
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import Airline, Route

DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"
DATA_PATH = Path(__file__).resolve().parent / "network_model.json"

VALID_MODELS = {"hub_and_spoke", "point_to_point"}


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    mapping = {k: v for k, v in data.items() if not k.startswith("_")}

    bad_values = {icao: v for icao, v in mapping.items() if v not in VALID_MODELS}
    if bad_values:
        raise SystemExit(f"Invalid network_model values: {bad_values}")

    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        routed_icaos = set(
            session.scalars(select(Route.airline_icao).distinct()).all()
        )

        missing = routed_icaos - mapping.keys()
        if missing:
            raise SystemExit(f"Missing classification for routed airlines: {sorted(missing)}")

        extra = mapping.keys() - routed_icaos
        if extra:
            raise SystemExit(f"Classification present for airlines with no routes: {sorted(extra)}")

        updated = 0
        for icao, model in mapping.items():
            airline = session.get(Airline, icao)
            if airline is None:
                raise SystemExit(f"Unknown airline ICAO in mapping: {icao}")
            airline.network_model = model
            updated += 1
        session.commit()

    print(f"Set network_model on {updated} airlines.")


if __name__ == "__main__":
    main()
