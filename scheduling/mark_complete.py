from models.schedule import Schedule
from models.base import with_session

from sqlalchemy.orm import Session

@with_session
def mark_flight_complete(Session: Session, schedule: Schedule) -> None:
    """Mark the given schedule (flight in schedule) as complete so that next flight can be moved on to.

    Args:
        Session (_type_): The database session
        schedule (Schedule): The schedule item to be marked as complete
    """
    completed_schedule = Session.query(Schedule).filter(Schedule.id == schedule.id).first()
    completed_schedule.status = "completed"

    next_schedule = Session.query(Schedule).filter(Schedule.day_no == schedule.day_no).filter(Schedule.flight_index == schedule.flight_index + 1).first()
    if next_schedule == None:
        print("Completed schedule was the last of the day")

        next_schedule = Session.query(Schedule).filter(Schedule.day_no == schedule.day_no + 1).filter(Schedule.flight_index == 0).first()

        if next_schedule == None:
            print("No remaining schedules")
            Session.commit()
            return None

    next_schedule.status = "current"

    Session.commit()