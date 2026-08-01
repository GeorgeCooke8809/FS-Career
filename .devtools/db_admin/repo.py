"""Per-table search/filter/CRUD helpers. Plain SQLAlchemy, one section per model.

Every search_* function returns (rows, total_count) so callers can paginate.
Every create_*/update_*/delete_* function lets IntegrityError propagate —
callers (screens/forms) are the boundary that talks to the user.
"""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from models import Aircraft, AircraftFamily, Airline, Airport, Route


# ---------------------------------------------------------------------------
# Airlines
# ---------------------------------------------------------------------------

def search_airlines(
    session: Session,
    text: str | None,
    country: str | None = None,
    has_logo: bool | None = None,
    network_model: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[Airline], int]:
    stmt = select(Airline)
    if text:
        like = f"%{text}%"
        stmt = stmt.where(
            or_(
                Airline.icao.ilike(like),
                Airline.iata.ilike(like),
                Airline.name.ilike(like),
                Airline.callsign.ilike(like),
                Airline.country.ilike(like),
            )
        )
    if country:
        stmt = stmt.where(Airline.country == country)
    if has_logo is not None:
        stmt = stmt.where(Airline.has_logo == has_logo)
    if network_model == "unset":
        stmt = stmt.where(Airline.network_model.is_(None))
    elif network_model is not None:
        stmt = stmt.where(Airline.network_model == network_model)
    stmt = stmt.order_by(Airline.icao)
    total = session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = session.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return list(rows), total or 0


def distinct_airline_countries(session: Session) -> list[str]:
    return session.execute(
        select(Airline.country).distinct().order_by(Airline.country)
    ).scalars().all()


def create_airline(session: Session, **fields) -> Airline:
    obj = Airline(**fields)
    session.add(obj)
    session.commit()
    return obj


def update_airline(session: Session, obj: Airline, **fields) -> Airline:
    for key, value in fields.items():
        setattr(obj, key, value)
    session.commit()
    return obj


def delete_airline(session: Session, obj: Airline) -> None:
    session.delete(obj)
    session.commit()


# ---------------------------------------------------------------------------
# Airports
# ---------------------------------------------------------------------------

def search_airports(
    session: Session, text: str | None, page: int = 1, page_size: int = 50
) -> tuple[list[Airport], int]:
    stmt = select(Airport)
    if text:
        like = f"%{text}%"
        stmt = stmt.where(
            or_(
                Airport.icao.ilike(like),
                Airport.iata.ilike(like),
                Airport.name.ilike(like),
                Airport.city.ilike(like),
                Airport.country.ilike(like),
            )
        )
    stmt = stmt.order_by(Airport.icao)
    total = session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = session.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return list(rows), total or 0


def create_airport(session: Session, **fields) -> Airport:
    obj = Airport(**fields)
    session.add(obj)
    session.commit()
    return obj


def update_airport(session: Session, obj: Airport, **fields) -> Airport:
    for key, value in fields.items():
        setattr(obj, key, value)
    session.commit()
    return obj


def delete_airport(session: Session, obj: Airport) -> None:
    session.delete(obj)
    session.commit()


# ---------------------------------------------------------------------------
# Aircraft Families
# ---------------------------------------------------------------------------

def search_aircraft_families(
    session: Session,
    text: str | None,
    category: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[AircraftFamily], int]:
    stmt = select(AircraftFamily)
    if text:
        like = f"%{text}%"
        stmt = stmt.where(
            or_(
                AircraftFamily.name.ilike(like),
                AircraftFamily.manufacturer.ilike(like),
            )
        )
    if category:
        stmt = stmt.where(AircraftFamily.category == category)
    stmt = stmt.order_by(AircraftFamily.name)
    total = session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = session.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return list(rows), total or 0


def create_aircraft_family(session: Session, **fields) -> AircraftFamily:
    obj = AircraftFamily(**fields)
    session.add(obj)
    session.commit()
    return obj


def update_aircraft_family(session: Session, obj: AircraftFamily, **fields) -> AircraftFamily:
    for key, value in fields.items():
        setattr(obj, key, value)
    session.commit()
    return obj


def delete_aircraft_family(session: Session, obj: AircraftFamily) -> None:
    session.delete(obj)
    session.commit()


# ---------------------------------------------------------------------------
# Aircraft
# ---------------------------------------------------------------------------

def search_aircraft(
    session: Session,
    text: str | None,
    family_id: int | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[Aircraft], int]:
    stmt = select(Aircraft)
    if text:
        like = f"%{text}%"
        stmt = stmt.where(
            or_(Aircraft.icao_type.ilike(like), Aircraft.name.ilike(like))
        )
    if family_id is not None:
        stmt = stmt.where(Aircraft.family_id == family_id)
    stmt = stmt.order_by(Aircraft.icao_type)
    total = session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = session.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return list(rows), total or 0


def create_aircraft(session: Session, **fields) -> Aircraft:
    obj = Aircraft(**fields)
    session.add(obj)
    session.commit()
    return obj


def update_aircraft(session: Session, obj: Aircraft, **fields) -> Aircraft:
    for key, value in fields.items():
        setattr(obj, key, value)
    session.commit()
    return obj


def delete_aircraft(session: Session, obj: Aircraft) -> None:
    session.delete(obj)
    session.commit()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def search_routes(
    session: Session,
    text: str | None,
    airline_icao: str | None = None,
    origin_icao: str | None = None,
    destination_icao: str | None = None,
    aircraft_icao_type: str | None = None,
    flight_number_synthetic: bool | None = None,
    schedule_synthetic: bool | None = None,
    aircraft_icao_type_synthetic: bool | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[Route], int]:
    stmt = select(Route)
    if text:
        like = f"%{text}%"
        stmt = stmt.join(Route.airline).join(
            Airport, Route.origin_icao == Airport.icao
        )
        stmt = stmt.where(
            or_(
                Route.flight_number.ilike(like),
                Airline.name.ilike(like),
                Airline.icao.ilike(like),
                Airport.name.ilike(like),
                Airport.icao.ilike(like),
                Airport.city.ilike(like),
            )
        )
    if airline_icao:
        stmt = stmt.where(Route.airline_icao == airline_icao)
    if origin_icao:
        stmt = stmt.where(Route.origin_icao == origin_icao)
    if destination_icao:
        stmt = stmt.where(Route.destination_icao == destination_icao)
    if aircraft_icao_type:
        stmt = stmt.where(Route.aircraft_icao_type == aircraft_icao_type)
    if flight_number_synthetic is not None:
        stmt = stmt.where(Route.flight_number_synthetic == flight_number_synthetic)
    if schedule_synthetic is not None:
        stmt = stmt.where(Route.schedule_synthetic == schedule_synthetic)
    if aircraft_icao_type_synthetic is not None:
        stmt = stmt.where(Route.aircraft_icao_type_synthetic == aircraft_icao_type_synthetic)
    stmt = stmt.order_by(Route.id)
    total = session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = session.execute(
        stmt.limit(page_size).offset((page - 1) * page_size)
    ).scalars().all()
    return list(rows), total or 0


def flight_number_exists(
    session: Session, airline_icao: str, flight_number: str, exclude_id: int | None = None
) -> bool:
    stmt = select(Route.id).where(
        Route.airline_icao == airline_icao, Route.flight_number == flight_number
    )
    if exclude_id is not None:
        stmt = stmt.where(Route.id != exclude_id)
    return session.execute(stmt.limit(1)).first() is not None


def create_route(session: Session, **fields) -> Route:
    obj = Route(**fields)
    session.add(obj)
    session.commit()
    return obj


def update_route(session: Session, obj: Route, **fields) -> Route:
    for key, value in fields.items():
        setattr(obj, key, value)
    session.commit()
    return obj


def delete_route(session: Session, obj: Route) -> None:
    session.delete(obj)
    session.commit()


# ---------------------------------------------------------------------------
# Reference-count helpers (used before delete to give a friendlier warning)
# ---------------------------------------------------------------------------

def count_routes_for_airline(session: Session, icao: str) -> int:
    return session.scalar(
        select(func.count()).select_from(Route).where(Route.airline_icao == icao)
    ) or 0


def count_routes_for_airport(session: Session, icao: str) -> int:
    return session.scalar(
        select(func.count()).select_from(Route).where(
            or_(Route.origin_icao == icao, Route.destination_icao == icao)
        )
    ) or 0


def count_routes_for_aircraft(session: Session, icao_type: str) -> int:
    return session.scalar(
        select(func.count()).select_from(Route).where(
            Route.aircraft_icao_type == icao_type
        )
    ) or 0


def count_aircraft_for_family(session: Session, family_id: int) -> int:
    return session.scalar(
        select(func.count()).select_from(Aircraft).where(
            Aircraft.family_id == family_id
        )
    ) or 0
