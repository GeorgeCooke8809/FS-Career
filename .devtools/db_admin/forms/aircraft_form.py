import customtkinter as ctk
from sqlalchemy import select

from db_admin import repo
from db_admin.forms.base_form import BaseRecordForm
from db_admin.widgets.searchable_combobox import SearchableCombobox
from models import AircraftFamily


class AircraftForm(BaseRecordForm):
    title_text = "Aircraft"

    def build_fields(self, parent: ctk.CTkScrollableFrame) -> None:
        row = 0
        self.add_label_row(parent, row, "ICAO Type *")
        self.icao_type_entry = ctk.CTkEntry(parent)
        self.icao_type_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.icao_type_entry.insert(0, self.record.icao_type)
            self.icao_type_entry.configure(state="disabled")
        row += 1

        self.add_label_row(parent, row, "Name *")
        self.name_entry = ctk.CTkEntry(parent)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.name_entry.insert(0, self.record.name)
        row += 1

        self.add_label_row(parent, row, "Family *")
        self.family_combo = SearchableCombobox(
            parent,
            self.session,
            fetch_fn=lambda sess: sess.execute(
                select(AircraftFamily).order_by(AircraftFamily.name)
            ).scalars().all(),
            display_fn=lambda f: f"{f.name} ({f.manufacturer})",
            value_fn=lambda f: f.id,
        )
        self.family_combo.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.family_combo.set_by_value(self.record.family_id)
        row += 1

    def validate(self) -> list[str]:
        errors = []
        icao_type = self.icao_type_entry.get().strip()
        if not icao_type:
            errors.append("ICAO Type is required.")
        elif len(icao_type) > 4:
            errors.append("ICAO Type must be at most 4 characters.")
        if not self.name_entry.get().strip():
            errors.append("Name is required.")
        if self.family_combo.get_value() is None:
            errors.append("Family must be chosen from the list.")
        return errors

    def save(self) -> None:
        fields = dict(
            name=self.name_entry.get().strip(),
            family_id=self.family_combo.get_value(),
        )
        if self.is_edit:
            repo.update_aircraft(self.session, self.record, **fields)
        else:
            repo.create_aircraft(
                self.session, icao_type=self.icao_type_entry.get().strip().upper(), **fields
            )
