import customtkinter as ctk
from sqlalchemy import select

from db_admin import repo
from db_admin.forms.route_form import RouteForm
from db_admin.screens.base_screen import BaseTableScreen
from db_admin.widgets.searchable_combobox import SearchableCombobox
from models import Aircraft, Airline, Airport


class RoutesScreen(BaseTableScreen):
    columns = ["Flight", "Airline", "Origin", "Destination", "Aircraft", "Dist (nm)"]
    page_size = 50

    def build_filters(self, parent: ctk.CTkFrame) -> None:
        self.airline_filter: str | None = None
        self.origin_filter: str | None = None
        self.destination_filter: str | None = None
        self.aircraft_filter: str | None = None
        self.flight_number_synthetic_filter: bool | None = None
        self.schedule_synthetic_filter: bool | None = None
        self.aircraft_synthetic_filter: bool | None = None

        for col, label in enumerate(["Airline", "Origin", "Destination", "Aircraft"]):
            ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11)).grid(
                row=0, column=col, sticky="w", padx=4
            )

        self.airline_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Airline).order_by(Airline.icao)).scalars().all(),
            display_fn=lambda a: f"{a.icao} — {a.name}",
            value_fn=lambda a: a.icao,
            width=160,
        )
        self.airline_combo.grid(row=1, column=0, padx=4)
        self.airline_combo.bind("<Return>", lambda _e: self._apply_route_filters())
        self.airline_combo.configure(command=lambda _v: self._apply_route_filters())

        self.origin_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Airport).order_by(Airport.icao)).scalars().all(),
            display_fn=lambda ap: f"{ap.icao} — {ap.city}",
            value_fn=lambda ap: ap.icao,
            width=160,
        )
        self.origin_combo.grid(row=1, column=1, padx=4)
        self.origin_combo.configure(command=lambda _v: self._apply_route_filters())

        self.destination_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Airport).order_by(Airport.icao)).scalars().all(),
            display_fn=lambda ap: f"{ap.icao} — {ap.city}",
            value_fn=lambda ap: ap.icao,
            width=160,
        )
        self.destination_combo.grid(row=1, column=2, padx=4)
        self.destination_combo.configure(command=lambda _v: self._apply_route_filters())

        self.aircraft_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Aircraft).order_by(Aircraft.icao_type)).scalars().all(),
            display_fn=lambda ac: f"{ac.icao_type} — {ac.name}",
            value_fn=lambda ac: ac.icao_type,
            width=160,
        )
        self.aircraft_combo.grid(row=1, column=3, padx=4)
        self.aircraft_combo.configure(command=lambda _v: self._apply_route_filters())

        for col, label in enumerate(["Flight #", "Schedule", "Aircraft Type"]):
            ctk.CTkLabel(parent, text=f"{label} synthetic?", font=ctk.CTkFont(size=11)).grid(
                row=2, column=col, sticky="w", padx=4, pady=(8, 0)
            )

        synthetic_values = ["All", "Synthetic only", "Real only"]

        self.flight_number_synthetic_menu = ctk.CTkOptionMenu(
            parent, values=synthetic_values, width=160,
            command=lambda v: self._on_synthetic_change("flight_number_synthetic_filter", v),
        )
        self.flight_number_synthetic_menu.set("All")
        self.flight_number_synthetic_menu.grid(row=3, column=0, padx=4)

        self.schedule_synthetic_menu = ctk.CTkOptionMenu(
            parent, values=synthetic_values, width=160,
            command=lambda v: self._on_synthetic_change("schedule_synthetic_filter", v),
        )
        self.schedule_synthetic_menu.set("All")
        self.schedule_synthetic_menu.grid(row=3, column=1, padx=4)

        self.aircraft_synthetic_menu = ctk.CTkOptionMenu(
            parent, values=synthetic_values, width=160,
            command=lambda v: self._on_synthetic_change("aircraft_synthetic_filter", v),
        )
        self.aircraft_synthetic_menu.set("All")
        self.aircraft_synthetic_menu.grid(row=3, column=2, padx=4)

        clear_btn = ctk.CTkButton(parent, text="Clear filters", width=100, command=self._clear_route_filters)
        clear_btn.grid(row=3, column=3, padx=4)

    def _on_synthetic_change(self, attr_name: str, value: str) -> None:
        setattr(self, attr_name, {"All": None, "Synthetic only": True, "Real only": False}[value])
        self.on_filter_change()

    def _apply_route_filters(self) -> None:
        self.airline_filter = self.airline_combo.get_value()
        self.origin_filter = self.origin_combo.get_value()
        self.destination_filter = self.destination_combo.get_value()
        self.aircraft_filter = self.aircraft_combo.get_value()
        self.on_filter_change()

    def _clear_route_filters(self) -> None:
        for combo in (self.airline_combo, self.origin_combo, self.destination_combo, self.aircraft_combo):
            combo.set("")
        self.airline_filter = self.origin_filter = self.destination_filter = self.aircraft_filter = None
        for menu in (
            self.flight_number_synthetic_menu, self.schedule_synthetic_menu, self.aircraft_synthetic_menu,
        ):
            menu.set("All")
        self.flight_number_synthetic_filter = None
        self.schedule_synthetic_filter = None
        self.aircraft_synthetic_filter = None
        self.on_filter_change()

    def fetch_rows(self, page: int):
        return repo.search_routes(
            self.session, self.search_text,
            airline_icao=self.airline_filter,
            origin_icao=self.origin_filter,
            destination_icao=self.destination_filter,
            aircraft_icao_type=self.aircraft_filter,
            flight_number_synthetic=self.flight_number_synthetic_filter,
            schedule_synthetic=self.schedule_synthetic_filter,
            aircraft_icao_type_synthetic=self.aircraft_synthetic_filter,
            page=page, page_size=self.page_size,
        )

    def format_row(self, obj) -> list[str]:
        return [
            f"{obj.airline_icao}{obj.flight_number}",
            obj.airline.name,
            obj.origin_icao,
            obj.destination_icao,
            obj.aircraft_icao_type,
            f"{obj.distance_nm:.0f}",
        ]

    def open_add_form(self) -> None:
        RouteForm(self, self.session, on_saved=self.refresh)

    def open_edit_form(self, obj) -> None:
        RouteForm(self, self.session, record=obj, on_saved=self.refresh)

    def do_delete(self, obj) -> None:
        repo.delete_route(self.session, obj)

    def record_label(self, obj) -> str:
        return f"{obj.airline_icao}{obj.flight_number} ({obj.origin_icao}→{obj.destination_icao})"
