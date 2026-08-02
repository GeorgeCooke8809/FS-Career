import customtkinter as ctk
from sqlalchemy.exc import IntegrityError


def friendly_message(
    error: IntegrityError, table_label: str = "this record", referenced_by: str = "other records"
) -> str:
    """Translate a raw SQLite IntegrityError into a message a non-DBA can act on."""
    raw = str(error.orig)

    if "FOREIGN KEY constraint failed" in raw:
        return (
            f"Cannot delete {table_label} — it is still referenced by one or more "
            f"{referenced_by}. Delete or reassign those first."
        )
    if "UNIQUE constraint failed" in raw:
        field = raw.split("UNIQUE constraint failed:", 1)[-1].strip()
        return f"That value is already in use — a record with a duplicate {field} already exists."
    if "CHECK constraint failed" in raw:
        constraint = raw.split("CHECK constraint failed:", 1)[-1].strip()
        return f"That value violates a database rule ({constraint}). Please check the field values."
    if "NOT NULL constraint failed" in raw:
        field = raw.split("NOT NULL constraint failed:", 1)[-1].strip()
        return f"Required field is missing: {field}"

    return raw


class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str):
        super().__init__(master)
        self.title(title)
        self.geometry("460x220")
        self.transient(master)
        self.grab_set()

        textbox = ctk.CTkTextbox(self, wrap="word")
        textbox.pack(padx=20, pady=(20, 12), fill="both", expand=True)
        textbox.insert("1.0", message)
        textbox.configure(state="disabled")

        ok_btn = ctk.CTkButton(self, text="OK", width=100, command=self.destroy)
        ok_btn.pack(pady=(0, 16))

        self.protocol("WM_DELETE_WINDOW", self.destroy)


def show_error(master, title: str, message: str) -> None:
    dialog = ErrorDialog(master, title, message)
    master.wait_window(dialog)
