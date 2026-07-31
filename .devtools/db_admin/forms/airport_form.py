import customtkinter as ctk

from db_admin import repo
from db_admin.forms.base_form import BaseRecordForm


class AirportForm(BaseRecordForm):
    title_text = "Airport"

    def build_fields(self, parent: ctk.CTkScrollableFrame) -> None:
        row = 0
        self.add_label_row(parent, row, "ICAO *")
        self.icao_entry = ctk.CTkEntry(parent)
        self.icao_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.icao_entry.insert(0, self.record.icao)
            self.icao_entry.configure(state="disabled")
        row += 1

        self.add_label_row(parent, row, "IATA")
        self.iata_entry = ctk.CTkEntry(parent)
        self.iata_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record and self.record.iata:
            self.iata_entry.insert(0, self.record.iata)
        row += 1

        self.add_label_row(parent, row, "Name *")
        self.name_entry = ctk.CTkEntry(parent)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.name_entry.insert(0, self.record.name)
        row += 1

        self.add_label_row(parent, row, "City *")
        self.city_entry = ctk.CTkEntry(parent)
        self.city_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.city_entry.insert(0, self.record.city)
        row += 1

        self.add_label_row(parent, row, "Country *")
        self.country_entry = ctk.CTkEntry(parent)
        self.country_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.country_entry.insert(0, self.record.country)
        row += 1

        self.add_label_row(parent, row, "Latitude *")
        self.lat_entry = ctk.CTkEntry(parent)
        self.lat_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record is not None:
            self.lat_entry.insert(0, str(self.record.latitude))
        row += 1

        self.add_label_row(parent, row, "Longitude *")
        self.lon_entry = ctk.CTkEntry(parent)
        self.lon_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record is not None:
            self.lon_entry.insert(0, str(self.record.longitude))
        row += 1

        self.add_label_row(parent, row, "Timezone *")
        self.timezone_entry = ctk.CTkEntry(parent)
        self.timezone_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.timezone_entry.insert(0, self.record.timezone)
        row += 1

    def _parse_float(self, text: str) -> float | None:
        try:
            return float(text.strip())
        except ValueError:
            return None

    def validate(self) -> list[str]:
        errors = []
        icao = self.icao_entry.get().strip()
        if not icao:
            errors.append("ICAO is required.")
        elif len(icao) > 4:
            errors.append("ICAO must be at most 4 characters.")
        if not self.name_entry.get().strip():
            errors.append("Name is required.")
        if not self.city_entry.get().strip():
            errors.append("City is required.")
        if not self.country_entry.get().strip():
            errors.append("Country is required.")
        if not self.timezone_entry.get().strip():
            errors.append("Timezone is required.")

        lat = self._parse_float(self.lat_entry.get())
        if lat is None:
            errors.append("Latitude must be a number.")
        elif not (-90 <= lat <= 90):
            errors.append("Latitude must be between -90 and 90.")

        lon = self._parse_float(self.lon_entry.get())
        if lon is None:
            errors.append("Longitude must be a number.")
        elif not (-180 <= lon <= 180):
            errors.append("Longitude must be between -180 and 180.")

        iata = self.iata_entry.get().strip()
        if iata and len(iata) > 3:
            errors.append("IATA must be at most 3 characters.")
        return errors

    def save(self) -> None:
        fields = dict(
            iata=self.iata_entry.get().strip().upper() or None,
            name=self.name_entry.get().strip(),
            city=self.city_entry.get().strip(),
            country=self.country_entry.get().strip(),
            latitude=float(self.lat_entry.get().strip()),
            longitude=float(self.lon_entry.get().strip()),
            timezone=self.timezone_entry.get().strip(),
        )
        if self.is_edit:
            repo.update_airport(self.session, self.record, **fields)
        else:
            repo.create_airport(self.session, icao=self.icao_entry.get().strip().upper(), **fields)
