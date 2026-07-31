import customtkinter as ctk
from sqlalchemy import select

from db_admin import repo
from db_admin.forms.aircraft_form import AircraftForm
from db_admin.screens.base_screen import BaseTableScreen
from models import AircraftFamily


class AircraftScreen(BaseTableScreen):
    columns = ["ICAO Type", "Name", "Family"]
    referenced_by_label = "Routes"

    def build_filters(self, parent: ctk.CTkFrame) -> None:
        self.family_filter: int | None = None
        families = self.session.execute(
            select(AircraftFamily).order_by(AircraftFamily.name)
        ).scalars().all()
        self._family_by_label = {f"{f.name} ({f.manufacturer})": f.id for f in families}
        self.family_menu = ctk.CTkOptionMenu(
            parent,
            values=["All"] + list(self._family_by_label.keys()),
            command=self._on_family_change,
        )
        self.family_menu.set("All")
        self.family_menu.pack(side="left")

    def _on_family_change(self, value: str) -> None:
        self.family_filter = None if value == "All" else self._family_by_label[value]
        self.on_filter_change()

    def fetch_rows(self, page: int):
        return repo.search_aircraft(
            self.session, self.search_text, family_id=self.family_filter,
            page=page, page_size=self.page_size,
        )

    def format_row(self, obj) -> list[str]:
        return [obj.icao_type, obj.name, obj.family.name]

    def open_add_form(self) -> None:
        AircraftForm(self, self.session, on_saved=self.refresh)

    def open_edit_form(self, obj) -> None:
        AircraftForm(self, self.session, record=obj, on_saved=self.refresh)

    def do_delete(self, obj) -> None:
        repo.delete_aircraft(self.session, obj)

    def record_label(self, obj) -> str:
        return f"{obj.icao_type} — {obj.name}"
