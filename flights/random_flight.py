from models import Route

def get_random_route(airline_icao: str, origin: str, max_length: int = 10_000, min_length: int = 0) -> Route:
    """Gets and returns the route object of a random flight for the airline from the given base

    Args:
        airline (str): The airline to generate a route for
        origin (str): The origin airport
        max_length (int, optional): The maximum duration (in minutes) of the flight. Defaults to 10_000.
        min_length (int, optional): The minimum duration (in minutes) of the flight. Defaults to 0.

    Returns:
        Route: _description_
    """