from models import Schedule, Route, Airport
import tkinter
import tkintermapview
from PIL import Image
import ui.theme as theme

class ScheduleMap(tkintermapview.TkinterMapView):
    def __init__(self, parent, schedules: list[Schedule]):
        super().__init__(parent, corner_radius=0) # ? May need to add width and height?

        self.canvas.configure(bg="#262626") # Changes the background of the map to the same colour as the sea
        self.set_tile_server("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}")

        self._create_widgets(schedules)

    def _create_widgets(self, schedules: list[Schedule]):
        markers = []
        self.top_left_corner = None
        self.bottom_right_corner = None

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

            route_markers.append(self.set_path([route_markers[0].position, route_markers[1].position], color=route_colour, width=3))

            markers.append(route_markers)

        if len(schedules) == 0:
            self.top_left_corner = [61.5738048, -18.9545160]
            self.bottom_right_corner = [24.2245723, 28.9458746]

        self.fit_bounding_box(tuple(self.top_left_corner), tuple(self.bottom_right_corner)) # TODO: Padding?

    def _update_corner_coordinates(self, coordinates: tuple[float, float]):
            if self.top_left_corner == None:
                self.top_left_corner = list(coordinates)
            if self.bottom_right_corner == None:
                self.bottom_right_corner = list(coordinates)

            if coordinates[0] > self.top_left_corner[0]:
                self.top_left_corner[0] = coordinates[0]
            elif coordinates[0] < self.bottom_right_corner[0]:
                self.bottom_right_corner[0] = coordinates[0]

            if coordinates[1] < self.top_left_corner[1]:
                self.top_left_corner[1] = coordinates[1]
            elif coordinates[1] > self.bottom_right_corner[1]:
                self.bottom_right_corner[1] = coordinates[1]