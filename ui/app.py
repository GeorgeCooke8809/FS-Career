import customtkinter
from ui.active_day_schedule import ActiveDaySchedule
from ui.map_widget import ScheduleMap
from utils import validation
from tkinter import messagebox
from models import Route, Schedule
from scheduling import create_schedule, get_current_day_schedule, delete_schedules_in_day_range
import logging

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x750")
        self.minsize(1000, 750)
        self.title("Random Flight Schedule Generator")

        self._create_widgets()

        self.mainloop()

    def _create_widgets(self):
        self.airline_entry = customtkinter.CTkEntry(self, placeholder_text="Airline ICAO")

        self.origin_entry = customtkinter.CTkEntry(self, placeholder_text="Origin ICAO")
        self.flight_count_entry = customtkinter.CTkEntry(self, placeholder_text="No. Flights") # Will have to validate is numeric

        self.min_flight_dur_entry = customtkinter.CTkEntry(self, placeholder_text="Min Duration (Mins)") # Will have to validate is numeric
        self.max_flight_dur_entry = customtkinter.CTkEntry(self, placeholder_text="Max Duration (Mins)") # Will have to validate is numeric

        self.generate_schedule_button = customtkinter.CTkButton(self, text="Generate Schedule", command=self._generate_schedule_click)

        self.content = ActiveDaySchedule(self, schedule=[])

        self.schedule_map = ScheduleMap(self, schedules=[])

        self._draw_widgets()

    def _draw_widgets(self):
        self.rowconfigure((0,1,2,3), weight=1, minsize=25)
        self.rowconfigure(4, weight=10_000)

        self.columnconfigure((0,1), weight=1)
        self.columnconfigure(2, weight=5)


        self.airline_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=2.5)

        self.origin_entry.grid(row=1, column=0, sticky="nsew", padx=5, pady=2.5)
        self.flight_count_entry.grid(row=1, column=1, sticky="nsew", padx=5, pady=2.5)

        self.min_flight_dur_entry.grid(row=2, column=0, sticky="nsew", padx=5, pady=2.5)
        self.max_flight_dur_entry.grid(row=2, column=1, sticky="nsew", padx=5, pady=2.5)

        self.generate_schedule_button.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=2.5)

        self.content.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.schedule_map.grid(row=0, column=2, rowspan=5, sticky="nsew")

    def _schedule_fail(self, message: str) -> None:
        messagebox.showerror("Schedule Error", message)
        return None

    def _generate_schedule_click(self):
        # Getting data
        airline_icao = self.airline_entry.get().upper()
        origin_icao = self.origin_entry.get().upper()
        no_flights = self.flight_count_entry.get()
        min_flight_dur = self.min_flight_dur_entry.get()
        max_flight_dur = self.max_flight_dur_entry.get()

        if min_flight_dur == "":
            min_flight_dur = "0"
        if max_flight_dur == "":
            max_flight_dur = "10000"


        # Validation
        if not validation.check_airline_icao_exists(airline_icao):
            return self._schedule_fail("Airline does not exist")

        if not validation.check_airport_icao_exists(origin_icao):
            return self._schedule_fail("Airport does not exist")

        values_to_check = [[no_flights, "Number of flights"], [min_flight_dur, "Minimum flight duration"], [max_flight_dur, "Maximum flight duration"]]

        for value, message in values_to_check:
            if not value.isnumeric():
                return self._schedule_fail(f"{message} must be numeric.")

        no_flights = int(no_flights)
        min_flight_dur = int(min_flight_dur)
        max_flight_dur = int(max_flight_dur)

        # TEMP: Delete current schedule data - this is only needed until flight tracking and marking flights as complete
        delete_schedules_in_day_range(start_day=0, end_day=0, career_id=0) # Delete schedule for day_no = 0

        try:
            create_schedule(career_id=0, airline_icao=airline_icao, origin=origin_icao, no_daily_flights=no_flights, min_flight_duration=min_flight_dur, max_flight_duration=max_flight_dur, no_days=1)
            print("Schedule successfully created.")
            schedule: list[Schedule] = get_current_day_schedule(0)
        except Exception as e:
            print(e)
            return self._schedule_fail("Something went wrong generating the schedule.")

        if schedule is None:
            return self._schedule_fail("Something went wrong generating the schedule.")

        print(schedule)

        self.content = ActiveDaySchedule(self, schedule=schedule)
        self.schedule_map = ScheduleMap(self, schedules=schedule)
        
        self.content.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.schedule_map.grid(row=0, column=2, rowspan=5, sticky="nsew")