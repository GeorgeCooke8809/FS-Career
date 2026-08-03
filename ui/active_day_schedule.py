import customtkinter
from models import Route
from ui.route_widget import RouteWidget

class ActiveDaySchedule(customtkinter.CTkScrollableFrame):
    def __init__(self, parent, schedule: list[Route]):
        super().__init__(parent)

        self._create_widgets(schedule)

    def _create_widgets(self, schedules):
        self.widgets: list[customtkinter.CTkFrame] = []

        for route in schedules:
            self.widgets.append(RouteWidget(self, route, "current"))

        self._draw_widgets()

    def _draw_widgets(self):
        self.columnconfigure(0, weight=1)

        for i, widget in enumerate(self.widgets):
            widget.grid(row=i, column=0, pady=5, sticky="nsew")