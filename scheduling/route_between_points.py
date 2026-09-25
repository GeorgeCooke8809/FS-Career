from models.route import Route
from models.base import with_session

def get_route_between_points(Session, airline_icao: str, origin: str, destination: str):
    """Gets the route between two points. Most useful for getting the return flight of a randomly generated flight.

    Args:
        airline_icao (str): The airline to search for the route of
        origin (str): The origin airport for the route (ICAO code)
        destination (str): The destination airport of the route (ICAO code)
    """

    return_route: Route = (
        Session.query(Route)
        .filter(Route.airline_icao == airline_icao)
        .filter(Route.origin_icao == origin)
        .filter(Route.destination_icao == destination)
        .first()
    )

    return return_route