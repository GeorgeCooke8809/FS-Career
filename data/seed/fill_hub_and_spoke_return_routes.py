"""Add missing return legs for hub_and_spoke airlines.

A hub-and-spoke carrier's network should let passengers get back from every
spoke it serves. This finds routes belonging to hub_and_spoke airlines whose
reverse (destination -> origin) doesn't exist, and inserts it: same aircraft
type and distance as the outbound leg (both are route-geometry facts, so
they're symmetric), a freshly synthesized flight number, and the same
synthetic flags as the outbound leg for aircraft type, plus synthetic
flight number/schedule (matching how all-synthetic routes are flagged
elsewhere - see memory/project_routes_import.md).
"""
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Airline, Route

DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"


def main() -> None:
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        hub_and_spoke_icaos = set(
            session.scalars(
                select(Airline.icao).where(Airline.network_model == "hub_and_spoke")
            ).all()
        )

        all_routes = session.scalars(select(Route)).all()
        pairs_by_airline: dict[str, set[tuple[str, str]]] = {}
        for r in all_routes:
            pairs_by_airline.setdefault(r.airline_icao, set()).add(
                (r.origin_icao, r.destination_icao)
            )

        next_flight_number: dict[str, int] = {}
        for icao in hub_and_spoke_icaos:
            nums = [
                int(n) for (n,) in session.execute(
                    select(Route.flight_number).where(Route.airline_icao == icao)
                )
                if n.isdigit()
            ]
            next_flight_number[icao] = max(nums, default=0) + 1

        added = 0
        for r in all_routes:
            if r.airline_icao not in hub_and_spoke_icaos:
                continue
            reverse_key = (r.destination_icao, r.origin_icao)
            if reverse_key in pairs_by_airline[r.airline_icao]:
                continue

            flight_number = str(next_flight_number[r.airline_icao])
            next_flight_number[r.airline_icao] += 1

            session.add(
                Route(
                    airline_icao=r.airline_icao,
                    origin_icao=r.destination_icao,
                    destination_icao=r.origin_icao,
                    aircraft_icao_type=r.aircraft_icao_type,
                    flight_number=flight_number,
                    distance_nm=r.distance_nm,
                    duration_minutes=r.duration_minutes,
                    flight_number_synthetic=True,
                    schedule_synthetic=True,
                    aircraft_icao_type_synthetic=r.aircraft_icao_type_synthetic,
                )
            )
            pairs_by_airline[r.airline_icao].add(reverse_key)
            added += 1

        session.commit()

    print(f"Added {added} return routes for hub_and_spoke airlines.")


if __name__ == "__main__":
    main()
