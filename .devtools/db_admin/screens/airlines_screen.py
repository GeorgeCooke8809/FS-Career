import customtkinter as ctk

from db_admin import repo
from db_admin.forms.airline_form import AirlineForm
from db_admin.screens.base_screen import BaseTableScreen
from db_admin.widgets.image_thumbnail import load_thumbnail


class AirlinesScreen(BaseTableScreen):
    columns = ["Logo", "ICAO", "IATA", "Name", "Callsign", "Country"]
    referenced_by_label = "Routes"

    def build_filters(self, parent: ctk.CTkFrame) -> None:
        self.country_filter: str | None = None
        self.has_logo_filter: bool | None = None

        countries = repo.distinct_airline_countries(self.session)
        self.country_menu = ctk.CTkOptionMenu(
            parent, values=["All Countries"] + countries, command=self._on_country_change, width=160,
        )
        self.country_menu.set("All Countries")
        self.country_menu.pack(side="left", padx=(0, 8))

        self.has_logo_menu = ctk.CTkOptionMenu(
            parent, values=["Logo: All", "Logo: Yes", "Logo: No"],
            command=self._on_has_logo_change, width=120,
        )
        self.has_logo_menu.set("Logo: All")
        self.has_logo_menu.pack(side="left")

    def _on_country_change(self, value: str) -> None:
        self.country_filter = None if value == "All Countries" else value
        self.on_filter_change()

    def _on_has_logo_change(self, value: str) -> None:
        self.has_logo_filter = {"Logo: All": None, "Logo: Yes": True, "Logo: No": False}[value]
        self.on_filter_change()

    def fetch_rows(self, page: int):
        return repo.search_airlines(
            self.session, self.search_text,
            country=self.country_filter, has_logo=self.has_logo_filter,
            page=page, page_size=self.page_size,
        )

    def format_row(self, obj) -> list[str]:
        return ["", obj.icao, obj.iata or "", obj.name, obj.callsign, obj.country]

    def cell_widgets(self) -> dict:
        return {0: self._logo_cell}

    def _logo_cell(self, parent, record) -> ctk.CTkLabel:
        image = load_thumbnail(record.logo_path, size=(32, 32)) if record.logo_path else None
        label = ctk.CTkLabel(parent, text="" if image else "-", image=image, width=40)
        label._image_ref = image  # keep a reference alive so Tk doesn't garbage-collect it
        return label

    def open_add_form(self) -> None:
        AirlineForm(self, self.session, on_saved=self.refresh)

    def open_edit_form(self, obj) -> None:
        AirlineForm(self, self.session, record=obj, on_saved=self.refresh)

    def do_delete(self, obj) -> None:
        repo.delete_airline(self.session, obj)

    def record_label(self, obj) -> str:
        return f"{obj.icao} — {obj.name}"
