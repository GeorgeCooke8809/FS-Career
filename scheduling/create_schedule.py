from models import Schedule, Route, Career
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from random import randint

from scheduling.generate_schedule import create_day_schedule

from models.base import with_session

"""
Uses generate_schedule.py to generate a schedule for the given number of days and saves it to the schedule database.
Use generate_schedule if looking to just create a schedule for a single day
"""

# TODO: Make new days push destination towards base one career implemented - currently runs risk of drifting away from base. It could be possible to do this in generate schedule instead of here.

@with_session
def create_schedule(Session: Session, career_id: int, airline_icao: str, origin: str, no_daily_flights: int, min_flight_duration: int = 0, max_flight_duration = 10_000, no_days:int = 30, min_layover_duration: int = 20, max_layover_duration: int = 45):
    if no_days == 0:
        return None

    current_day = Session.query(Career.current_day).filter(Career.id == career_id).scalar()

    if current_day == None:
            raise ValueError("Career does not exist")

    current_max_schedule = Session.query(Schedule.day_no).filter(Schedule.career_id == career_id).order_by(Schedule.day_no.desc()).scalar()
    if current_max_schedule == None: current_max_schedule = -1 # Edge case for if no schedule has been created in career

    if current_day <= current_max_schedule: # This will mean that the date will have to be incremented BEFORE the creation of a new schedule when career is implemented
        raise ValueError("Cannot make new schedule, the old schedule has not yet been completed!")


    day_schedules: list[list[Route]] = [create_day_schedule(airline_icao=airline_icao, origin=origin, no_flights=no_daily_flights, min_flight_duration=min_flight_duration, max_flight_duration=max_flight_duration)] # A 2D array of all day schedules created.

    for _ in range(no_days-1):
        day_origin = day_schedules[-1][-1].destination_icao
        day_schedules += [create_day_schedule(airline_icao=airline_icao, origin=day_origin, no_flights=no_daily_flights, min_flight_duration=min_flight_duration, max_flight_duration=max_flight_duration)]

    for i, day in enumerate(day_schedules):
        random_hour = randint(0, 23)
        random_minute = 5 * randint(0, 11) # Minute of schedule start rounded to nearest 5 mins
        next_flight_start = datetime.min.replace(hour=random_hour, minute=random_minute) # generate departure time of first flight in day schedule on the minimum possible date value

        flight_index = -1

        for route in day:
            flight_index += 1

            if i == 0 and flight_index == 0: status = "current"
            else: status = "future"

            new_schedule = Schedule(day_no=current_day, flight_index=flight_index, route=route, departure_time_utc=next_flight_start.time(), status=status, career_id=career_id)

            layover_duration = max(min_layover_duration, min(5 * round(randint(min_layover_duration, max_layover_duration + 1) / 5), max_layover_duration)) # random layover duration rounded to nearest 5 minutes kept within bounds of min/max
            next_flight_start += timedelta(minutes=route.duration_minutes + layover_duration)

            Session.add(new_schedule)

        current_day += 1