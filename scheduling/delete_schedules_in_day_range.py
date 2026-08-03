from models import Schedule
from models.base import with_session

from sqlalchemy.orm import Session

@with_session
def delete_schedules_in_day_range(Session: Session, start_day: int, end_day: int, career_id: int) -> None:
    (
        Session.query(Schedule)
        .filter(Schedule.career_id == career_id)
        .filter(Schedule.day_no >= start_day)
        .filter(Schedule.day_no <= end_day)
        .delete()
    )