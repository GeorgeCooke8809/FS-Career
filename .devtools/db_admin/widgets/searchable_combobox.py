from typing import Callable, TypeVar

import customtkinter as ctk
from sqlalchemy.orm import Session

T = TypeVar("T")

# CTkComboBox's dropdown is a native tkinter.Menu rebuilt from scratch on every
# configure(values=...); posting that menu takes seconds once it holds more
# than a couple hundred items (measured ~3.7s at 732 items, ~11s at 10,030).
# Capping what's ever handed to the menu keeps it responsive no matter how
# large the backing table is (airports alone is 10,030 rows).
MAX_DROPDOWN_ITEMS = 30


class SearchableCombobox(ctk.CTkComboBox):
    """A CTkComboBox wrapper for picking a foreign-key target by display text
    (e.g. "DAL — Delta Air Lines") while storing/returning the underlying PK.

    Fetches the related table once at construction, but only ever shows up to
    MAX_DROPDOWN_ITEMS in the dropdown itself (whichever match the current
    search text) — the full list is kept in memory for lookup/filtering, never
    handed to the native Tk menu at once. `get_value()` returns None unless
    the typed text exactly matches a known display string, so a form can force
    "must pick from the list".
    """

    def __init__(
        self,
        master,
        session: Session,
        fetch_fn: Callable[[Session], list[T]],
        display_fn: Callable[[T], str],
        value_fn: Callable[[T], object],
        **kwargs,
    ):
        self._session = session
        self._fetch_fn = fetch_fn
        self._display_fn = display_fn
        self._value_fn = value_fn
        self._display_to_value: dict[str, object] = {}
        self._all_displays: list[str] = []

        super().__init__(master, values=[], **kwargs)
        self.bind("<KeyRelease>", self._on_key_release)
        self.refresh_options()

    def refresh_options(self) -> None:
        records = self._fetch_fn(self._session)
        self._display_to_value = {
            self._display_fn(record): self._value_fn(record) for record in records
        }
        self._all_displays = sorted(self._display_to_value.keys())
        self.configure(values=self._all_displays[:MAX_DROPDOWN_ITEMS])

    def _on_key_release(self, _event) -> None:
        typed = self.get()
        if not typed:
            self.configure(values=self._all_displays[:MAX_DROPDOWN_ITEMS])
            return
        filtered = [d for d in self._all_displays if typed.lower() in d.lower()]
        self.configure(values=(filtered or self._all_displays)[:MAX_DROPDOWN_ITEMS])

    def get_value(self):
        return self._display_to_value.get(self.get())

    def set_by_value(self, value) -> None:
        for display, v in self._display_to_value.items():
            if v == value:
                self.set(display)
                return
        self.set("")
