import customtkinter as ctk

from db_admin.db import get_session
from db_admin.screens.aircraft_families_screen import AircraftFamiliesScreen
from db_admin.screens.aircraft_screen import AircraftScreen
from db_admin.screens.airlines_screen import AirlinesScreen
from db_admin.screens.airports_screen import AirportsScreen
from db_admin.screens.routes_screen import RoutesScreen

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

TABS = [
    ("Airlines", AirlinesScreen),
    ("Airports", AirportsScreen),
    ("Aircraft Families", AircraftFamiliesScreen),
    ("Aircraft", AircraftScreen),
    ("Routes", RoutesScreen),
]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FS Career — DB Admin")
        self.geometry("1200x750")

        self.session = get_session()

        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        for name, screen_cls in TABS:
            tab = tabview.add(name)
            screen = screen_cls(tab, self.session)
            screen.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        self.session.close()
        self.destroy()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
