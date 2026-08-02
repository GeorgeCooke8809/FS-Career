import customtkinter as ctk

from db_admin import repo
from db_admin.forms.base_form import BaseRecordForm
from models.aircraft_family import CATEGORIES


class AircraftFamilyForm(BaseRecordForm):
    title_text = "Aircraft Family"

    def build_fields(self, parent: ctk.CTkScrollableFrame) -> None:
        row = 0
        self.add_label_row(parent, row, "Name *")
        self.name_entry = ctk.CTkEntry(parent)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.name_entry.insert(0, self.record.name)
        row += 1

        self.add_label_row(parent, row, "Manufacturer *")
        self.manufacturer_entry = ctk.CTkEntry(parent)
        self.manufacturer_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.manufacturer_entry.insert(0, self.record.manufacturer)
        row += 1

        self.add_label_row(parent, row, "Category *")
        self.category_menu = ctk.CTkOptionMenu(parent, values=list(CATEGORIES))
        self.category_menu.grid(row=row, column=1, sticky="ew", pady=8)
        self.category_menu.set(self.record.category if self.record else CATEGORIES[0])
        row += 1

    def validate(self) -> list[str]:
        errors = []
        if not self.name_entry.get().strip():
            errors.append("Name is required.")
        if not self.manufacturer_entry.get().strip():
            errors.append("Manufacturer is required.")
        return errors

    def save(self) -> None:
        fields = dict(
            name=self.name_entry.get().strip(),
            manufacturer=self.manufacturer_entry.get().strip(),
            category=self.category_menu.get(),
        )
        if self.is_edit:
            repo.update_aircraft_family(self.session, self.record, **fields)
        else:
            repo.create_aircraft_family(self.session, **fields)
