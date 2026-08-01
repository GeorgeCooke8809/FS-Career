from models import Airline
from models import Route
from models.base import with_session
from scheduling import get_random_route, get_route_between_points
import logging

# TODO: Make schedule redirect to base on first flight if not already when career mode implemented - At the moment, the logic will try to redirect to wherever the origin is for the end of the schedule. It is possible that this will not be the base of the player.
# TODO: Make type rating constraint - at the moment, routes from any aircraft can be generated. This should be fixed

@with_session
def create_schedule(Session, airline_icao: str, origin: str, no_flights: int, min_flight_duration: int = 0, max_flight_duration = 10_000) -> list[Route]:
    airline: Airline = (
        Session.query(Airline)
        .filter(Airline.icao == airline_icao)
        .first()
    )

    if no_flights == 1:
        logging.info(f"Getting random route for single flight schedule")
        return [get_random_route(airline_icao=airline_icao, origin=origin, min_duration=min_flight_duration, max_duration=max_flight_duration)]
    elif airline.network_model == "hub_and_spoke" or no_flights == 2:
        logging.info(f"Using hub and spoke model for {airline_icao} with {no_flights} flights")
        return create_hub_and_spoke_schedule(airline_icao, origin, no_flights, min_flight_duration=min_flight_duration, max_flight_duration=max_flight_duration)
    elif airline.network_model == "point_to_point":
        logging.info(f"Using point to point model for {airline_icao}")
        return create_point_to_point_schedule(airline_icao, origin, no_flights, min_flight_duration=min_flight_duration, max_flight_duration=max_flight_duration)
    elif airline.network_model == None:
        raise ValueError("Airline has not been assigned network_model")
    else:
        raise ValueError(f"Invalid network_model in database: {airline.network_model} for {airline.icao}")


def create_hub_and_spoke_schedule(airline_icao: str, origin: str, no_flights: int, min_flight_duration: int, max_flight_duration: int) -> list[Route]:
    schedule = []
    total_duration = 0

    while len(schedule) < no_flights and total_duration < 600: # Check if schedule shorter than desired and pilot is under legal flying hour limit (10 hours)
        outbound_route: Route = get_random_route(airline_icao=airline_icao, origin=origin, min_duration=min_flight_duration, max_duration=max_flight_duration)
        temp_total_duration = total_duration + outbound_route.duration_minutes

        if temp_total_duration > 600 and len(schedule) > 0: # do not add the new route if it will break time limits unless it is the first route
            break

        total_duration = temp_total_duration
        schedule += [outbound_route]

        return_route: Route = get_route_between_points(airline_icao=airline_icao, origin=outbound_route.destination_icao, destination=origin) # database is guarded in the hub and spoke model so that this will never return none

        if return_route == None:
            raise ValueError("Return route returned none - this likely indicates a corrupted hub and spoke model airline in the database")

        temp_total_duration = total_duration + return_route.duration_minutes

        if temp_total_duration > 600 or len(schedule) == no_flights: # do not add the new route if it will break time or flight limits. This allows for ending away from base to simulate layovers
            break

        total_duration = temp_total_duration
        schedule += [return_route]

    return schedule


def create_point_to_point_schedule(airline_icao: str, origin: str, no_flights: int, min_flight_duration: int, max_flight_duration: int, attempts_remaining: int = 5) -> list[Route]:
    # ? Make this use a reverse dijkstra to find the best route instead of messy solution - is it really needed, the current systems works well in all tests
    if attempts_remaining == 0:
        raise ValueError("Sparse point to point network, borderline impossible to create route")

    schedule: list[Route] = [get_random_route(airline_icao=airline_icao, origin=origin, min_duration=min_flight_duration, max_duration=max_flight_duration)]
    total_duration = 0

    while len(schedule) < no_flights - 1 and total_duration < 500: # Check if schedule shorter than desired and pilot is under legal flying hour limit (10 hours) - budgeted for and extra hop and 100 mins to return to base, if this budget is exceeded the law (in the game) is broken. This is messy and ought to be fixed later
        route: Route = get_random_route(airline_icao=airline_icao, origin=schedule[-1].destination_icao, min_duration=min_flight_duration, max_duration=max_flight_duration)
        schedule += [route]

    return_to_base = get_route_between_points(airline_icao=airline_icao, origin=schedule[-1].destination_icao, destination=origin)
    rtb_attempts = 0

    while return_to_base == None and rtb_attempts <= 10:
        schedule[-1] = get_random_route(airline_icao=airline_icao, origin=schedule[-2].destination_icao, min_duration=min_flight_duration, max_duration=max_flight_duration)

        return_to_base = get_route_between_points(airline_icao=airline_icao, origin=schedule[-1].destination_icao, destination=origin)

        rtb_attempts += 1

    if rtb_attempts == 11: # This would mean that route connection failed - reverts to empty schedule to try again
        logging.info("Schedule generation failed to link up. Restarting...")
        schedule = create_point_to_point_schedule(airline_icao, origin, no_flights, min_flight_duration=min_flight_duration, max_flight_duration=max_flight_duration, attempts_remaining=attempts_remaining-1)
    else:
        schedule += [return_to_base]

    total_duration = 0
    for route in schedule:
        total_duration += route.duration_minutes

    logging.info(f"{total_duration = }")

    if total_duration > 600:
        logging.info("Schedule was too long. Restarting ...")
        schedule = create_point_to_point_schedule(airline_icao, origin, no_flights, min_flight_duration=min_flight_duration, max_flight_duration=max_flight_duration, attempts_remaining=attempts_remaining-1)

    return schedule