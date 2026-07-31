from tkinter import filedialog

import customtkinter as ctk

from db_admin import repo
from db_admin.db import LOGOS_DIR
from db_admin.forms.base_form import BaseRecordForm
from db_admin.widgets.error_dialog import show_error
from db_admin.widgets.image_thumbnail import delete_logo, load_thumbnail, save_logo

IMAGE_FILETYPES = [
    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
    ("All files", "*.*"),
]


class AirlineForm(BaseRecordForm):
    title_text = "Airline"

    def build_fields(self, parent: ctk.CTkScrollableFrame) -> None:
        self._has_logo = bool(self.record.has_logo) if self.record else False

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

        self.add_label_row(parent, row, "Callsign *")
        self.callsign_entry = ctk.CTkEntry(parent)
        self.callsign_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.callsign_entry.insert(0, self.record.callsign)
        row += 1

        self.add_label_row(parent, row, "Country *")
        self.country_entry = ctk.CTkEntry(parent)
        self.country_entry.grid(row=row, column=1, sticky="ew", pady=8)
        if self.record:
            self.country_entry.insert(0, self.record.country)
        row += 1

        self.add_label_row(parent, row, "Logo")
        logo_col = ctk.CTkFrame(parent, fg_color="transparent")
        logo_col.grid(row=row, column=1, sticky="w", pady=8)

        self.logo_label = ctk.CTkLabel(logo_col, text="No logo", width=96, height=96)
        self.logo_label.pack(side="left", padx=(0, 12))

        btn_col = ctk.CTkFrame(logo_col, fg_color="transparent")
        btn_col.pack(side="left")
        self.upload_btn = ctk.CTkButton(btn_col, text="Upload Logo...", command=self._on_upload)
        self.upload_btn.pack(anchor="w", pady=(0, 4))
        self.remove_btn = ctk.CTkButton(
            btn_col, text="Remove Logo", fg_color="gray40", command=self._on_remove
        )
        self.remove_btn.pack(anchor="w")

        self._logo_image = None
        self._refresh_thumbnail()
        self._update_upload_state()

        if not self.is_edit:
            self.icao_entry.bind("<KeyRelease>", lambda _e: self._update_upload_state())

    def _current_icao(self) -> str:
        return self.icao_entry.get().strip().upper()

    def _update_upload_state(self) -> None:
        icao = self._current_icao()
        state = "normal" if icao else "disabled"
        self.upload_btn.configure(state=state)
        self.remove_btn.configure(state=state if self._has_logo else "disabled")

    def _refresh_thumbnail(self) -> None:
        icao = self._current_icao()
        path = LOGOS_DIR / f"{icao}.png" if (self._has_logo and icao) else None
        image = load_thumbnail(path)
        self._logo_image = image
        if image:
            self.logo_label.configure(image=image, text="")
        else:
            self.logo_label.configure(image=None, text="No logo")

    def _on_upload(self) -> None:
        icao = self._current_icao()
        if not icao:
            show_error(self, "Missing ICAO", "Enter the airline's ICAO code before uploading a logo.")
            return
        path = filedialog.askopenfilename(title="Choose a logo image", filetypes=IMAGE_FILETYPES)
        if not path:
            return
        try:
            save_logo(icao, path)
        except Exception as error:
            show_error(self, "Upload failed", f"Could not read that file as an image.\n{error}")
            return
        self._has_logo = True
        self._refresh_thumbnail()
        self._update_upload_state()

    def _on_remove(self) -> None:
        icao = self._current_icao()
        if icao:
            delete_logo(icao)
        self._has_logo = False
        self._refresh_thumbnail()
        self._update_upload_state()

    def validate(self) -> list[str]:
        errors = []
        icao = self._current_icao()
        if not icao:
            errors.append("ICAO is required.")
        elif len(icao) > 3:
            errors.append("ICAO must be at most 3 characters.")
        if not self.name_entry.get().strip():
            errors.append("Name is required.")
        if not self.callsign_entry.get().strip():
            errors.append("Callsign is required.")
        if not self.country_entry.get().strip():
            errors.append("Country is required.")
        iata = self.iata_entry.get().strip()
        if iata and len(iata) > 2:
            errors.append("IATA must be at most 2 characters.")
        return errors

    def save(self) -> None:
        fields = dict(
            iata=self.iata_entry.get().strip().upper() or None,
            name=self.name_entry.get().strip(),
            callsign=self.callsign_entry.get().strip(),
            country=self.country_entry.get().strip(),
            has_logo=self._has_logo,
        )
        if self.is_edit:
            repo.update_airline(self.session, self.record, **fields)
        else:
            repo.create_airline(self.session, icao=self._current_icao(), **fields)
