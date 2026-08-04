from models import Schedule, Route, Airport
import tkinter
import tkintermapview
import ui.theme as theme

class ScheduleMap(tkintermapview.TkinterMapView):
    def __init__(self, parent, schedules: list[Schedule]):
        super().__init__(parent, corner_radius=0) # ? May need to add width and height?

        self._create_widgets(schedules)

    def _create_widgets(self, schedules: list[Schedule]):
        markers = []
        self.top_left_corner = [1.1, -1.1]
        self.bottom_right_corner = [-1.1, 1.1]

        for schedule in schedules:
            route_markers = []

            if schedule.status == "complete":
                route_colour = theme.Colours.ROUTE_CARD_COMPLETED_SIDE
            elif schedule.status == "current":
                route_colour = theme.Colours.ROUTE_CARD_CURRENT_SIDE
            elif schedule.status == "future":
                route_colour = theme.Colours.ROUTE_CARD_FUTURE_SIDE
            else:
                raise ValueError(f"Schedule status is invalid. {schedule}")

            route = schedule.route

            departure_airport = route.origin
            self._update_corner_coordinates((departure_airport.latitude, departure_airport.longitude))

            arrival_airport = route.destination
            self._update_corner_coordinates((arrival_airport.latitude, arrival_airport.longitude))

            route_markers.append(self.set_marker(departure_airport.latitude, departure_airport.longitude))
            route_markers.append(self.set_marker(arrival_airport.latitude, arrival_airport.longitude))

            route_markers.append(self.set_path([route_markers[0].position, route_markers[1].position], color=route_colour))

            markers.append(route_markers)

        self.set_zoom(19)
        self.fit_bounding_box(tuple(self.top_left_corner), tuple(self.bottom_right_corner)) # TODO: Padding?

    def _update_corner_coordinates(self, coordinates: tuple[float, float]):
            if coordinates[0] > self.top_left_corner[0]:
                self.top_left_corner[0] = coordinates[0]
            elif coordinates[0] < self.bottom_right_corner[0]:
                self.bottom_right_corner[0] = coordinates[0]

            if coordinates[1] < self.top_left_corner[1]:
                self.top_left_corner[1] = coordinates[1]
            elif coordinates[1] > self.bottom_right_corner[1]:
                self.bottom_right_corner[1] = coordinates[1]