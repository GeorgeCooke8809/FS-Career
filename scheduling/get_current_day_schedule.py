from models import Schedule, Career, Route
from models.base import with_session

from sqlalchemy.orm import Session, joinedload

@with_session
def get_current_day_schedule(Session: Session, career_id: int) -> list[Schedule]:
    current_day = Session.query(Career.current_day).filter(Career.id == career_id).scalar()

    if current_day == None:
        raise ValueError(f"Career with id: {career_id} does not exist.")


    return (
        Session.query(Schedule)
        .options(
            joinedload(Schedule.route).joinedload(Route.origin),
            joinedload(Schedule.route).joinedload(Route.destination),
        )
        .filter(Schedule.career_id == career_id)
        .filter(Schedule.day_no == current_day)
        .order_by(Schedule.flight_index.asc())
        .all()
    )