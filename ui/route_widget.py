import customtkinter
from models import Route, Schedule, Aircraft
from PIL import Image
import sys, os
import ui.theme as theme
from datetime import timedelta, time, datetime, timezone
from zoneinfo import ZoneInfo
from utils import timezones
from webbrowser import open

class RouteWidget(customtkinter.CTkFrame):
    def __init__(self, parent, schedule: Schedule, height: int = 90):
        super().__init__(parent, corner_radius=0, height=height)
        self.grid_propagate(False)

        self._create_widgets(schedule, height)

        if schedule.status == "current":
            route = schedule.route
            
            airline = route.airline
            airline_iata = airline.iata
            flight_no = route.flight_number
            aircraft = route.aircraft
            aircraft_type = aircraft.icao_type
            origin = route.origin_icao
            destination = route.destination_icao
    
            departure_time = schedule.departure_time_utc
            departure_hour = departure_time.strftime("%H")
            departure_minute = departure_time.strftime("%M")
    
            simbrief_link = f"https://dispatch.simbrief.com/options/custom?airline={airline_iata}&fltnum={flight_no}&type={aircraft_type}&orig={origin}&dest={destination}&deph={departure_hour}&depm={departure_minute}"
            
            self._bind_click_recursive(self, lambda _ : open(simbrief_link))

    def _create_widgets(self, schedule: Schedule, height: int):
        if schedule.status == "completed":
            side_colour = theme.Colours.ROUTE_CARD_COMPLETED_SIDE
        elif schedule.status == "current":
            side_colour = theme.Colours.ROUTE_CARD_CURRENT_SIDE

        elif schedule.status == "future":
            side_colour = theme.Colours.ROUTE_CARD_FUTURE_SIDE

        self.left_colour = customtkinter.CTkFrame(self, fg_color=side_colour, width=5, corner_radius=0)
        self.content = RouteContent(self, schedule)
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

    def _bind_click_recursive(self, widget, function):
        widget.bind("<Button-1>", function)
        widget.configure(cursor="hand2")

        for child in widget.winfo_children():
            self._bind_click_recursive(child, function)

class RouteContent(customtkinter.CTkFrame):
    # TODO: Fix: Sometimes different ICAO codes take up different widths and shift the plane icon
    def __init__(self, parent, schedule: Schedule):
        super().__init__(parent, corner_radius=0)

        self._create_widgets(schedule)

    def _create_widgets(self, schedule: Schedule):
        route = schedule.route
        hours = route.duration_minutes // 60
        minutes = route.duration_minutes % 60

        anchor_date = datetime.now(timezone.utc)

        departure_datetime_utc = anchor_date.replace(hour=schedule.departure_time_utc.hour, minute=schedule.departure_time_utc.minute)
        arrival_datetime_utc = departure_datetime_utc + timedelta(minutes=route.duration_minutes)

        departure_timezone: ZoneInfo = timezones.get_airport_timezone(route.origin_icao)
        destination_timezone: ZoneInfo = timezones.get_airport_timezone(route.destination_icao)

        departure_datetime_local = departure_datetime_utc.astimezone(departure_timezone)
        arrival_datetime_local = arrival_datetime_utc.astimezone(destination_timezone)

        script_dir = sys.path[0]
        aircraft_logo_dir = os.path.join(script_dir, ".\\src\\aircraft_icon.png")

        # TOP ROW
        self.departure_local = customtkinter.CTkLabel(self, text=f"{departure_datetime_local.strftime("%H:%M")} local", font=theme.Fonts.route_card_subheader())
        self.flight_duration = customtkinter.CTkLabel(self, text=f"{hours:02}:{minutes:02}", font=theme.Fonts.route_card_subheader(), text_color=theme.Colours.ROUTE_CARD_ON_TIME_FONT) # TODO: Make this reflect the simulator time compared to departure time - waiting for simulator sync
        self.arrival_local = customtkinter.CTkLabel(self, text=f"{arrival_datetime_local.strftime("%H:%M")} local", font=theme.Fonts.route_card_subheader())

        # MIDDLE ROW
        self.departure_icao = customtkinter.CTkLabel(self, text=route.origin_icao, font=theme.Fonts.route_card_airport_icao())

        aircraft_logo = customtkinter.CTkImage(light_image=Image.open(aircraft_logo_dir).convert("RGBA"), size=(30, 30))
        self.aircraft_logo = customtkinter.CTkLabel(self, image=aircraft_logo, text="", fg_color="transparent")

        self.arrival_icao = customtkinter.CTkLabel(self, text=route.destination_icao, font=theme.Fonts.route_card_airport_icao())

        # BOTTOM ROW
        self.departure_utc = customtkinter.CTkLabel(self, text=f"{departure_datetime_utc.strftime("%H:%M")} UTC", font=theme.Fonts.route_card_subheader())
        self.callsign = customtkinter.CTkLabel(self, text=f"{route.airline_icao}{route.flight_number}", font=theme.Fonts.route_card_subheader())
        self.arrival_utc = customtkinter.CTkLabel(self, text=f"{arrival_datetime_utc.strftime("%H:%M")} UTC", font=theme.Fonts.route_card_subheader())

        self._draw_widgets()

    def _draw_widgets(self):
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self.columnconfigure((0,1,2), weight=1)

        self.departure_local.grid(row=0, column=0, sticky="nsew")
        self.flight_duration.grid(row=0, column=1, sticky="nsew")
        self.arrival_local.grid(row=0, column=2, sticky="nsew")

        self.departure_icao.grid(row=1, column=0, sticky="nsew")
        self.aircraft_logo.grid(row=1, column=1, sticky="nsew")
        self.arrival_icao.grid(row=1, column=2, sticky="nsew")

        self.departure_utc.grid(row=2, column=0, sticky="nsew")
        self.callsign.grid(row=2, column=1, sticky="nsew")
        self.arrival_utc.grid(row=2, column=2, sticky="nsew")