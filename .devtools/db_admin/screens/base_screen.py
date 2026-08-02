import customtkinter as ctk
from sqlalchemy.exc import IntegrityError

from db_admin.widgets.confirm_dialog import confirm
from db_admin.widgets.error_dialog import friendly_message, show_error
from db_admin.widgets.pager import Pager
from db_admin.widgets.record_table import RecordTable

SEARCH_DEBOUNCE_MS = 300


class BaseTableScreen(ctk.CTkFrame):
    """Shared search/filter/table/pager/add skeleton. Subclasses supply the
    per-table pieces (columns, data fetching, row formatting, forms) via the
    hooks below rather than re-implementing layout.
    """

    columns: list[str] = []
    page_size: int = 50

    def __init__(self, master, session):
        super().__init__(master, fg_color="transparent")
        self.session = session
        self.page = 1
        self.search_text: str | None = None
        self._search_after_id: str | None = None

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)

        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search...", width=240)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        self.filter_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        self.filter_frame.pack(side="left", padx=(0, 10))
        self.build_filters(self.filter_frame)

        add_btn = ctk.CTkButton(top_bar, text="+ Add", width=90, command=self.open_add_form)
        add_btn.pack(side="right")

        self.table = RecordTable(
            self,
            columns=self.columns,
            on_edit=self.open_edit_form,
            on_delete=self.delete_record,
            cell_widget_factories=self.cell_widgets(),
        )
        self.table.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.pager = Pager(self, on_page_change=self._on_page_change)
        self.pager.pack(pady=(0, 10))

        self.refresh()

    # -- Hooks for subclasses -------------------------------------------------

    def fetch_rows(self, page: int):
        """Return (rows, total_count) for the given page, honoring current
        search text / filter state held on self."""
        raise NotImplementedError

    def format_row(self, obj) -> list[str]:
        raise NotImplementedError

    def cell_widgets(self) -> dict:
        return {}

    def build_filters(self, parent: ctk.CTkFrame) -> None:
        pass

    def open_add_form(self) -> None:
        raise NotImplementedError

    def open_edit_form(self, obj) -> None:
        raise NotImplementedError

    def do_delete(self, obj) -> None:
        raise NotImplementedError

    def record_label(self, obj) -> str:
        return str(obj)

    referenced_by_label: str = "other records"

    # -- Search / paging wiring ------------------------------------------------

    def _on_search_key(self, _event) -> None:
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(SEARCH_DEBOUNCE_MS, self._apply_search)

    def _apply_search(self) -> None:
        self.search_text = self.search_entry.get() or None
        self.page = 1
        self.refresh()

    def on_filter_change(self) -> None:
        """Subclasses' filter widgets should call this after updating filter state."""
        self.page = 1
        self.refresh()

    def _on_page_change(self, page: int) -> None:
        self.page = page
        self.refresh()

    # -- Delete flow -------------------------------------------------------

    def delete_record(self, obj) -> None:
        if not confirm(self, f"Delete {self.record_label(obj)}? This cannot be undone."):
            return
        try:
            self.do_delete(obj)
        except IntegrityError as error:
            self.session.rollback()
            show_error(self, "Delete failed", friendly_message(
                error, self.record_label(obj), self.referenced_by_label
            ))
            return
        rows, _total = self.fetch_rows(self.page)
        if not rows and self.page > 1:
            self.page -= 1
        self.refresh()

    # -- Rendering -----------------------------------------------------------

    def refresh(self) -> None:
        rows, total = self.fetch_rows(self.page)
        self.table.set_rows(rows, self.format_row)
        self.pager.update_state(self.page, self.page_size, total)
