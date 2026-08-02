import customtkinter
from models import Route
from PIL import Image
import sys, os
import ui.theme as theme

class RouteWidget(customtkinter.CTkFrame):
    def __init__(self, parent, route: Route, flight_status: str, height: int = 90):
        super().__init__(parent, corner_radius=0, height=height)
        self.grid_propagate(False)

        self._create_widgets(route, flight_status, height)

    def _create_widgets(self, route: Route, flight_status: str, height: int):
        if flight_status == "completed":
            side_colour = theme.Colours.ROUTE_CARD_COMPLETED_SIDE
        elif flight_status == "current":
            side_colour = theme.Colours.ROUTE_CARD_CURRENT_SIDE
        elif flight_status == "future":
            side_colour = theme.Colours.ROUTE_CARD_FUTURE_SIDE

        self.left_colour = customtkinter.CTkFrame(self, fg_color=side_colour, width=5, corner_radius=0)
        self.content = RouteContent(self, route)
        self.right_colour = customtkinter.CTkFrame(self, fg_color=side_colour, width=5, corner_radius=0)

        self._draw_widgets()

    def _draw_widgets(self):
        self.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1, minsize=1)
        self.columnconfigure(1, weight=1000)
        self.columnconfigure(2, weight=1, minsize=1)

        self.left_colour.grid(row=0, column=0, sticky="nsew")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.right_colour.grid(row=0, column=2, sticky="nsew")

class RouteContent(customtkinter.CTkFrame):
    # TODO: Fix: Sometimes different ICAO codes take up different widths and shift the plane icon
    def __init__(self, parent, route: Route):
        super().__init__(parent, corner_radius=0)

        self._create_widgets(route)

    def _create_widgets(self, route: Route):
        hours = route.duration_minutes // 60
        minutes = route.duration_minutes % 60

        script_dir = sys.path[0]
        aircraft_logo_dir = os.path.join(script_dir, ".\\src\\aircraft_icon.png")

        # TOP ROW
        self.departure_local = customtkinter.CTkLabel(self, text="PLACE", font=theme.Fonts.route_card_subheader())
        self.flight_duration = customtkinter.CTkLabel(self, text=f"{hours:02}:{minutes:02}", font=theme.Fonts.route_card_subheader(), text_color=theme.Colours.ROUTE_CARD_ON_TIME_FONT) # TODO: Make this reflect the simulator time compared to departure time - waiting for simulator sync
        self.arrival_local = customtkinter.CTkLabel(self, text="PLACE", font=theme.Fonts.route_card_subheader())

        # MIDDLE ROW
        self.departure_icao = customtkinter.CTkLabel(self, text=route.origin_icao, font=theme.Fonts.route_card_airport_icao())

        aircraft_logo = customtkinter.CTkImage(light_image=Image.open(aircraft_logo_dir).convert("RGBA"), size=(30, 30))
        self.aircraft_logo = customtkinter.CTkLabel(self, image=aircraft_logo, text="", fg_color="transparent")

        self.arrival_icao = customtkinter.CTkLabel(self, text=route.destination_icao, font=theme.Fonts.route_card_airport_icao())

        # BOTTOM ROW
        self.departure_utc = customtkinter.CTkLabel(self, text="PLACE", font=theme.Fonts.route_card_subheader())
        self.callsign = customtkinter.CTkLabel(self, text=f"{route.airline_icao}{route.flight_number}", font=theme.Fonts.route_card_subheader())
        self.arrival_utc = customtkinter.CTkLabel(self, text="PLACE", font=theme.Fonts.route_card_subheader())

        self._draw_widgets()

    def _draw_widgets(self):
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self.columnconfigure((0,1,2), weight=1)

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