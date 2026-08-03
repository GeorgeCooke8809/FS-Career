from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from models.base import with_session
from models import Airport

@with_session
def get_airport_timezone(Session: Session, airport_icao: str) -> ZoneInfo:
    timezone = (
        Session.query(Airport.timezone)
        .filter(Airport.icao == airport_icao)
        .scalar()
    )

    return ZoneInfo(timezone)