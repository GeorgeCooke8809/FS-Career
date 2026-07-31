from typing import Callable

import customtkinter as ctk


class Pager(ctk.CTkFrame):
    """Prev/Next + 'Page N of M (T total)' control. Purely presentational —
    the owning screen tracks the actual page number and re-fetches on change.
    """

    def __init__(self, master, on_page_change: Callable[[int], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_page_change = on_page_change
        self.page = 1
        self.total_pages = 1

        self.prev_btn = ctk.CTkButton(self, text="< Prev", width=80, command=self._go_prev)
        self.prev_btn.pack(side="left", padx=4)

        self.label = ctk.CTkLabel(self, text="Page 1 of 1 (0 total)")
        self.label.pack(side="left", padx=12)

        self.next_btn = ctk.CTkButton(self, text="Next >", width=80, command=self._go_next)
        self.next_btn.pack(side="left", padx=4)

    def update_state(self, page: int, page_size: int, total: int) -> None:
        self.page = page
        self.total_pages = max(1, (total + page_size - 1) // page_size)
        self.label.configure(text=f"Page {self.page} of {self.total_pages} ({total} total)")
        self.prev_btn.configure(state="normal" if self.page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.page < self.total_pages else "disabled")

    def _go_prev(self) -> None:
        if self.page > 1:
            self.on_page_change(self.page - 1)

    def _go_next(self) -> None:
        if self.page < self.total_pages:
            self.on_page_change(self.page + 1)
