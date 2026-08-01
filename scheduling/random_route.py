from models.route import Route
from models.base import with_session
from sqlalchemy.sql.expression import func

@with_session
def get_random_route(Session, airline_icao: str, origin: str, max_duration: int, min_duration: int) -> Route:
    """Gets and returns the route object of a random flight for the airline from the given base

    Args:
        airline (str): The airline to generate a route for
        origin (str): The origin airport (ICAO code). Most useful for flights from a set base airport or in a mesh airline
        max_duration (int, optional): The maximum duration (in minutes) of the flight. Defaults to 10_000.
        min_duration (int, optional): The minimum duration (in minutes) of the flight. Defaults to 0.

    Returns:
        Route: _description_
    """

    random_route: Route = (
        Session.query(Route)
        .filter(Route.airline_icao == airline_icao)
        .filter(Route.origin_icao == origin)
        .filter(Route.duration_minutes.between(min_duration, max_duration))
        .order_by(func.random())
        .first()
    )

    return random_route