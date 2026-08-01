import customtkinter
from models import Route
from PIL import Image
import sys, os

class RouteWidget(customtkinter.CTkFrame):
    def __init__(self, parent, route: Route, flight_status: str):
        super().__init__(parent, corner_radius=0)

        self._create_widgets(route, flight_status)

    def _create_widgets(self, route: Route, flight_status: str):
        if flight_status == "completed":
            side_colour = "#ffffff"
        elif flight_status == "current":
            side_colour = "#ffffff"
        elif flight_status == "future":
            side_colour = "#ffffff"

        self.left_colour = customtkinter.CTkFrame(fg_color=side_colour)
        self.content = RouteContent(route)
        self.right_colour = customtkinter.CTkFrame(fg_color=side_colour)

        self._draw_widgets()

    def _draw_widgets(self):
        self.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1, minsize=10)
        self.columnconfigure(1, weight=1000)
        self.columnconfigure(2, weight=1, minsize=10)

        self.left_colour.grid(row=0, column=0, sticky="nsew")
        self.content.grid(row=0, column=1)
        self.right_colour.grid(row=0, column=2, sticky="nsew")

class RouteContent(customtkinter.CTkFrame):
    def __init__(self, parent, route: Route):
        super().__init__(parent)

        self._create_widgets(route)

    def _create_widgets(self, route: Route):
        hours = route.duration_minutes // 60
        minutes = route.duration_minutes % 60

        script_dir = sys.path[0]
        aircraft_logo_dir = os.path.join(script_dir, "../src/aircraft_icon.png")

        # TOP ROW
        self.departure_local = customtkinter.CTkLabel(self, text="PLACE")
        self.flight_duration = customtkinter.CTkLabel(self, text=f"{hours:02}:{minutes}")
        self.arrival_local = customtkinter.CTkLabel(self, text="PLACE")

        # MIDDLE ROW
        self.departure_icao = customtkinter.CTkLabel(self, text=route.origin_icao)

        aircraft_logo = customtkinter.CTkImage(light_image=Image.open(aircraft_logo_dir), size=(30, 30))
        self.aircraft_logo = customtkinter.CTkLabel(self, image=aircraft_logo, text="")

        self.arrival_icao = customtkinter.CTkLabel(self, text=route.destination_icao)

        # BOTTOM ROW
        self.departure_utc = customtkinter.CTkLabel(self, text="PLACE")
        self.callsign = customtkinter.CTkLabel(self, text=f"{route.airline_icao}{route.flight_number}")
        self.arrival_utc = customtkinter.CTkLabel(self, text="PLACE")

        self._draw_widgets()

    def _draw_widgets(self):
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self.departure_local.grid(row=0, column=0)
        self.flight_duration.grid(row=0, column=1)
        self.arrival_local.grid(row=0, column=2)

        self.departure_icao.grid(row=1, column=0)
        self.aircraft_logo.grid(row=1, column=1)
        self.arrival_icao.grid(row=1, column=2)

        self.departure_utc.grid(row=2, column=0)
        self.callsign.grid(row=2, column=1)
        self.arrival_utc.grid(row=2, column=2)

        self.columnconfigure((0,1,2), weight=1)