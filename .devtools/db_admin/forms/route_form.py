from datetime import datetime

import customtkinter as ctk
from sqlalchemy import select

from db_admin import repo
from db_admin.forms.base_form import BaseRecordForm
from db_admin.widgets.searchable_combobox import SearchableCombobox
from models import Aircraft, Airline, Airport


class RouteForm(BaseRecordForm):
    title_text = "Route"

    def build_fields(self, parent: ctk.CTkScrollableFrame) -> None:
        row = 0

        self.add_label_row(parent, row, "Airline *")
        self.airline_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Airline).order_by(Airline.icao)).scalars().all(),
            display_fn=lambda a: f"{a.icao} — {a.name}",
            value_fn=lambda a: a.icao,
        )
        self.airline_combo.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.airline_combo.set_by_value(self.record.airline_icao)
        row += 1

        self.add_label_row(parent, row, "Origin Airport *")
        self.origin_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Airport).order_by(Airport.icao)).scalars().all(),
            display_fn=lambda ap: f"{ap.icao} ({ap.iata or '—'}) — {ap.city}",
            value_fn=lambda ap: ap.icao,
        )
        self.origin_combo.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.origin_combo.set_by_value(self.record.origin_icao)
        row += 1

        self.add_label_row(parent, row, "Destination Airport *")
        self.destination_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Airport).order_by(Airport.icao)).scalars().all(),
            display_fn=lambda ap: f"{ap.icao} ({ap.iata or '—'}) — {ap.city}",
            value_fn=lambda ap: ap.icao,
        )
        self.destination_combo.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.destination_combo.set_by_value(self.record.destination_icao)
        row += 1

        self.add_label_row(parent, row, "Aircraft Type *")
        self.aircraft_combo = SearchableCombobox(
            parent, self.session,
            fetch_fn=lambda s: s.execute(select(Aircraft).order_by(Aircraft.icao_type)).scalars().all(),
            display_fn=lambda ac: f"{ac.icao_type} — {ac.name}",
            value_fn=lambda ac: ac.icao_type,
        )
        self.aircraft_combo.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.aircraft_combo.set_by_value(self.record.aircraft_icao_type)
        row += 1

        self.add_label_row(parent, row, "Flight Number *")
        self.flight_number_entry = ctk.CTkEntry(parent)
        self.flight_number_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.flight_number_entry.insert(0, self.record.flight_number)
        row += 1

        self.add_label_row(parent, row, "Distance (nm) *")
        self.distance_entry = ctk.CTkEntry(parent)
        self.distance_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.distance_entry.insert(0, str(self.record.distance_nm))
        row += 1

        self.add_label_row(parent, row, "Departure (HH:MM UTC) *")
        self.departure_entry = ctk.CTkEntry(parent, placeholder_text="HH:MM")
        self.departure_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.departure_entry.insert(0, self.record.departure_time_utc.strftime("%H:%M"))
        row += 1

        self.add_label_row(parent, row, "Duration (minutes) *")
        self.duration_entry = ctk.CTkEntry(parent)
        self.duration_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.duration_entry.insert(0, str(self.record.duration_minutes))
        row += 1

        self.flight_number_synthetic_var = ctk.BooleanVar(
            value=self.record.flight_number_synthetic if self.record else True
        )
        ctk.CTkCheckBox(
            parent, text="Flight number is synthetic", variable=self.flight_number_synthetic_var
        ).grid(row=row, column=1, sticky="w", pady=4)
        row += 1

        self.schedule_synthetic_var = ctk.BooleanVar(
            value=self.record.schedule_synthetic if self.record else True
        )
        ctk.CTkCheckBox(
            parent, text="Schedule is synthetic", variable=self.schedule_synthetic_var
        ).grid(row=row, column=1, sticky="w", pady=4)
        row += 1

        self.aircraft_synthetic_var = ctk.BooleanVar(
            value=self.record.aircraft_icao_type_synthetic if self.record else False
        )
        ctk.CTkCheckBox(
            parent, text="Aircraft type is synthetic", variable=self.aircraft_synthetic_var
        ).grid(row=row, column=1, sticky="w", pady=4)
        row += 1

    def _parse_time(self):
        try:
            return datetime.strptime(self.departure_entry.get().strip(), "%H:%M").time()
        except ValueError:
            return None

    def validate(self) -> list[str]:
        errors = []

        airline_icao = self.airline_combo.get_value()
        origin_icao = self.origin_combo.get_value()
        destination_icao = self.destination_combo.get_value()
        aircraft_type = self.aircraft_combo.get_value()

        if airline_icao is None:
            errors.append("Airline must be chosen from the list.")
        if origin_icao is None:
            errors.append("Origin airport must be chosen from the list.")
        if destination_icao is None:
            errors.append("Destination airport must be chosen from the list.")
        if aircraft_type is None:
            errors.append("Aircraft type must be chosen from the list.")
        if origin_icao is not None and origin_icao == destination_icao:
            errors.append("Origin and destination airports must be different.")

        flight_number = self.flight_number_entry.get().strip()
        if not flight_number:
            errors.append("Flight number is required.")
        elif airline_icao is not None:
            exclude_id = self.record.id if self.is_edit else None
            if repo.flight_number_exists(self.session, airline_icao, flight_number, exclude_id):
                errors.append("This airline already has a route with that flight number.")

        try:
            distance = float(self.distance_entry.get().strip())
            if distance <= 0:
                errors.append("Distance must be greater than 0.")
        except ValueError:
            errors.append("Distance must be a number.")

        try:
            duration = int(self.duration_entry.get().strip())
            if duration <= 0:
                errors.append("Duration must be greater than 0.")
        except ValueError:
            errors.append("Duration must be a whole number of minutes.")

        if self._parse_time() is None:
            errors.append("Departure time must be in HH:MM 24-hour format.")

        return errors

    def save(self) -> None:
        fields = dict(
            airline_icao=self.airline_combo.get_value(),
            origin_icao=self.origin_combo.get_value(),
            destination_icao=self.destination_combo.get_value(),
            aircraft_icao_type=self.aircraft_combo.get_value(),
            flight_number=self.flight_number_entry.get().strip(),
            distance_nm=float(self.distance_entry.get().strip()),
            departure_time_utc=self._parse_time(),
            duration_minutes=int(self.duration_entry.get().strip()),
            flight_number_synthetic=self.flight_number_synthetic_var.get(),
            schedule_synthetic=self.schedule_synthetic_var.get(),
            aircraft_icao_type_synthetic=self.aircraft_synthetic_var.get(),
        )
        if self.is_edit:
            repo.update_route(self.session, self.record, **fields)
        else:
            repo.create_route(self.session, **fields)
