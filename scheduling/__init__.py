"""Module for the selection of random and return routes.

### Includes:
    get_random_routes
    get_route_between_points
    create_day_schedule - Creates a list of routes for a day
    create_schedule - Creates a schedule for the given number of days (with times of departure) and saves it to db
    get_current_day_schedule
    delete_schedules_in_day_range
"""

from scheduling.random_route import get_random_route
from scheduling.route_between_points import get_route_between_points
from scheduling.generate_schedule import create_day_schedule
from scheduling.create_schedule import create_schedule
from scheduling.get_current_day_schedule import get_current_day_schedule
from scheduling.delete_schedules_in_day_range import delete_schedules_in_day_range