from models.schedule import Schedule
from models.base import with_session

from sqlalchemy.orm import Session

@with_session
def mark_flight_complete(Session: Session, schedule: Schedule):
    """Mark the given schedule (flight in schedule) as complete so that next flight can be moved on to.

    Args:
        Session (_type_): The database session
        schedule (Schedule): The schedule item to be marked as complete
    """
    schedule = Session.query(Schedule).filter(Schedule.id == schedule.id).first()

    schedule.status = "completed"
    Session.commit()