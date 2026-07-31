from typing import Callable

import customtkinter as ctk
from sqlalchemy.exc import IntegrityError

from db_admin.widgets.error_dialog import friendly_message, show_error


class BaseRecordForm(ctk.CTkToplevel):
    """Add/Edit skeleton. `record=None` means Add mode; `record=<instance>`
    means Edit mode. Subclasses build their own fields in build_fields() and
    read them back in collect_fields(); this class wires Save/Cancel and
    handles validation + IntegrityError fallback so each concrete form only
    deals with its own fields.
    """

    title_text = "Record"

    def __init__(self, master, session, record=None, on_saved: Callable[[], None] | None = None):
        super().__init__(master)
        self.session = session
        self.record = record
        self.on_saved = on_saved
        self.is_edit = record is not None

        self.title(f"{'Edit' if self.is_edit else 'Add'} {self.title_text}")
        self.geometry("480x520")
        self.transient(master)
        self.grab_set()

        self.fields_frame = ctk.CTkScrollableFrame(self)
        self.fields_frame.pack(fill="both", expand=True, padx=16, pady=16)
        self.fields_frame.grid_columnconfigure(1, weight=1)

        self.build_fields(self.fields_frame)
        if self.is_edit:
            self.populate(record)

        button_row = ctk.CTkFrame(self, fg_color="transparent")
        button_row.pack(pady=(0, 16))

        cancel_btn = ctk.CTkButton(
            button_row, text="Cancel", width=100, fg_color="gray40", command=self.destroy
        )
        cancel_btn.pack(side="left", padx=8)

        save_btn = ctk.CTkButton(button_row, text="Save", width=100, command=self.on_save)
        save_btn.pack(side="left", padx=8)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # -- Hooks for subclasses -------------------------------------------------

    def build_fields(self, parent: ctk.CTkScrollableFrame) -> None:
        raise NotImplementedError

    def populate(self, record) -> None:
        """Fill widgets from an existing record. Default no-op — most forms
        set widget values directly in build_fields when record is not None."""

    def validate(self) -> list[str]:
        return []

    def save(self) -> None:
        """Perform the create/update via repo.py. Subclass implements."""
        raise NotImplementedError

    # -- Save flow -----------------------------------------------------------

    def on_save(self) -> None:
        errors = self.validate()
        if errors:
            show_error(self, "Validation error", "\n".join(errors))
            return
        try:
            self.save()
        except IntegrityError as error:
            self.session.rollback()
            show_error(self, "Database error", friendly_message(error))
            return
        if self.on_saved:
            self.on_saved()
        self.destroy()

    # -- Small layout helper for subclasses -----------------------------------

    def add_label_row(self, parent: ctk.CTkScrollableFrame, row: int, label_text: str) -> int:
        label = ctk.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=0, sticky="ne", padx=(0, 12), pady=8)
        return row
