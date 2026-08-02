import customtkinter as ctk

from db_admin import repo
from db_admin.forms.aircraft_family_form import AircraftFamilyForm
from db_admin.screens.base_screen import BaseTableScreen
from models.aircraft_family import CATEGORIES


class AircraftFamiliesScreen(BaseTableScreen):
    columns = ["Name", "Manufacturer", "Category"]
    referenced_by_label = "Aircraft"

    def build_filters(self, parent: ctk.CTkFrame) -> None:
        self.category_filter: str | None = None
        self.category_menu = ctk.CTkOptionMenu(
            parent, values=["All"] + list(CATEGORIES), command=self._on_category_change
        )
        self.category_menu.set("All")
        self.category_menu.pack(side="left")

    def _on_category_change(self, value: str) -> None:
        self.category_filter = None if value == "All" else value
        self.on_filter_change()

    def fetch_rows(self, page: int):
        return repo.search_aircraft_families(
            self.session, self.search_text, category=self.category_filter,
            page=page, page_size=self.page_size,
        )

    def format_row(self, obj) -> list[str]:
        return [obj.name, obj.manufacturer, obj.category]

    def open_add_form(self) -> None:
        AircraftFamilyForm(self, self.session, on_saved=self.refresh)

    def open_edit_form(self, obj) -> None:
        AircraftFamilyForm(self, self.session, record=obj, on_saved=self.refresh)

    def do_delete(self, obj) -> None:
        repo.delete_aircraft_family(self.session, obj)

    def record_label(self, obj) -> str:
        return f"{obj.name} ({obj.manufacturer})"
