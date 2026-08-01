import customtkinter
from models import Route
from ui.route_widget import RouteWidget

class ActiveDaySchedule(customtkinter.CTkScrollableFrame):
    def __init__(self, parent, schedule: list[Route]):
        super().__init__(parent)

        self._create_widgets(schedule)

    def _create_widgets(self, schedule):
        self.widgets: list[customtkinter.CTkFrame] = []

        for route in schedule:
            self.widgets.append(RouteWidget(route, "current"))

        self._draw_widgets()

    def _draw_widgets(self):
        for i, widget in enumerate(self.widgets):
            widget.grid(row=i, column=0)