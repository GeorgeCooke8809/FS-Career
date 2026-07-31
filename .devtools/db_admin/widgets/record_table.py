from typing import Any, Callable

import customtkinter as ctk

ROW_BG_EVEN = ("gray92", "gray20")
ROW_BG_ODD = ("gray86", "gray15")


class RecordTable(ctk.CTkScrollableFrame):
    """A CTkScrollableFrame-based data grid. CustomTkinter has no native grid
    widget, so this builds one from a header row of labels plus one grid row
    per record. Callers pass in the current page's records only — this widget
    does not paginate itself, it just renders whatever `set_rows` is given.
    """

    def __init__(
        self,
        master,
        columns: list[str],
        on_edit: Callable[[Any], None],
        on_delete: Callable[[Any], None],
        cell_widget_factories: dict[int, Callable[[ctk.CTkFrame, Any], ctk.CTkBaseClass]] | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.columns = columns
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.cell_widget_factories = cell_widget_factories or {}

        n_cols = len(columns) + 2  # + Edit, Delete action columns
        for col in range(n_cols):
            self.grid_columnconfigure(col, weight=1 if col < len(columns) else 0)

        self._build_header()
        self._row_widgets: list[ctk.CTkBaseClass] = []

    def _build_header(self) -> None:
        for col, name in enumerate(self.columns):
            label = ctk.CTkLabel(self, text=name, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=col, sticky="w", padx=8, pady=(4, 8))
        ctk.CTkLabel(self, text="", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=len(self.columns), pady=(4, 8)
        )
        ctk.CTkLabel(self, text="", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=len(self.columns) + 1, pady=(4, 8)
        )

    def clear_rows(self) -> None:
        for widget in self._row_widgets:
            widget.destroy()
        self._row_widgets = []

    def set_rows(self, records: list, formatter: Callable[[Any], list[str]]) -> None:
        self.clear_rows()
        for row_index, record in enumerate(records):
            grid_row = row_index + 1
            bg = ROW_BG_EVEN if row_index % 2 == 0 else ROW_BG_ODD
            cells = formatter(record)

            for col, value in enumerate(cells):
                factory = self.cell_widget_factories.get(col)
                if factory is not None:
                    widget = factory(self, record)
                else:
                    widget = ctk.CTkLabel(self, text=str(value), fg_color=bg, anchor="w")
                widget.grid(row=grid_row, column=col, sticky="ew", padx=8, pady=2)
                self._row_widgets.append(widget)

            edit_btn = ctk.CTkButton(
                self, text="Edit", width=60, fg_color="gray40",
                command=lambda r=record: self.on_edit(r),
            )
            edit_btn.grid(row=grid_row, column=len(self.columns), padx=4, pady=2)
            self._row_widgets.append(edit_btn)

            delete_btn = ctk.CTkButton(
                self, text="Delete", width=60, fg_color="#b3261e", hover_color="#8c1d17",
                command=lambda r=record: self.on_delete(r),
            )
            delete_btn.grid(row=grid_row, column=len(self.columns) + 1, padx=4, pady=2)
            self._row_widgets.append(delete_btn)

        if not records:
            empty_label = ctk.CTkLabel(self, text="No records found.", text_color="gray60")
            empty_label.grid(row=1, column=0, columnspan=len(self.columns) + 2, pady=20)
            self._row_widgets.append(empty_label)
