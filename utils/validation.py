from models import Airline, Route, Aircraft, Airport
from models.base import with_session

@with_session
def check_airline_icao_exists(Session, airline_icao: str) -> bool:
    result = (
        Session.query(Airline)
        .filter(Airline.icao == airline_icao)
        .first()
    )

    if result == None: # Airline not in database
        return False
    
    return True

@with_session
def check_airport_icao_exists(Session, airport_icao: str) -> bool:
    result = (
        Session.query(Airport)
        .filter(Airport.icao == airport_icao)
        .first()
    )

    if result == None: # Airport does not exist in database
        return False

    return True